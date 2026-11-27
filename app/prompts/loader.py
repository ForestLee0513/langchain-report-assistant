import datetime as dt
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from app.core.logger import get_logger

logger = get_logger(__name__)

# cwd가 아니라 이 파일 위치 기준
PROMPT_DIR = Path(__file__).resolve().parent
SUPPORTED_SUFFIXES = (".md", ".txt")

# <이름>_<날짜>_<버전>  (이름에 '_'가 있어도 오른쪽 끝부터 해석)
_FILENAME_RE = re.compile(
    r"^(?P<name>.+)_(?P<date>\d{8}|\d{4}-\d{2}-\d{2})_[vV]?(?P<version>\d+(?:\.\d+)*)$"
)


@dataclass(frozen=True)
class PromptFile:
    path: Path
    name: str
    date: dt.date | None          # 규칙 없는 파일을 확장자로 직접 지정한 경우 None
    version: tuple[int, ...]

    @property
    def version_str(self) -> str:
        return ".".join(map(str, self.version))

    @property
    def sort_key(self) -> tuple:
        # 날짜 우선, 같은 날짜면 버전. 버전은 숫자로 비교 (1.10 > 1.9)
        return (self.date, self.version)


def _parse(path: Path) -> PromptFile | None:
    """규칙에 맞는 파일이면 PromptFile, 아니면 None."""
    if path.suffix.lower() not in SUPPORTED_SUFFIXES:
        return None
    m = _FILENAME_RE.match(path.stem)
    if not m:
        return None

    raw = m["date"]
    try:
        date = dt.datetime.strptime(raw, "%Y-%m-%d" if "-" in raw else "%Y%m%d").date()
    except ValueError:           # 20261399 같은 존재하지 않는 날짜
        return None

    version = tuple(int(x) for x in m["version"].split("."))
    return PromptFile(path=path, name=m["name"], date=date, version=version)


def _parse_version(value: str) -> tuple[int, ...]:
    try:
        return tuple(int(x) for x in value.strip().lstrip("vV").split("."))
    except ValueError:
        raise ValueError(f"invalid version: {value!r} (예: '1', 'v1.2')") from None


def _safe_target(name: str) -> Path:
    base = PROMPT_DIR.resolve()
    target = (base / name).resolve()
    if not target.is_relative_to(base):      # "../../.env" 차단
        raise ValueError(f"prompt path escapes prompt dir: {name!r}")
    return target


def resolve_prompt(name: str, version: str | None = None) -> PromptFile:
    """이름(+선택 버전)에 해당하는 프롬프트 파일을 찾는다. 기본은 가장 최신."""
    target = _safe_target(name)

    # 1) 확장자까지 명시하면 그 파일을 그대로 사용 (규칙 준수 여부와 무관)
    if target.suffix.lower() in SUPPORTED_SUFFIXES:
        if not target.is_file():
            raise FileNotFoundError(f"prompt file not found: {target}")
        parsed = _parse(target)
        return parsed or PromptFile(path=target, name=target.stem, date=None, version=())

    # 2) 이름만 주면 폴더를 스캔해서 같은 이름의 파일 중 최신을 선택
    directory, stem = target.parent, target.name
    if not directory.is_dir():
        raise FileNotFoundError(f"prompt dir not found: {directory}")

    matched: list[PromptFile] = []
    ignored: list[str] = []
    for p in sorted(directory.iterdir()):
        if not p.is_file() or p.suffix.lower() not in SUPPORTED_SUFFIXES:
            continue
        pf = _parse(p)
        if pf is not None:
            if pf.name == stem:
                matched.append(pf)
        elif p.stem.startswith(stem + "_"):
            ignored.append(p.name)           # 이름은 비슷한데 규칙에 안 맞는 파일

    if ignored:
        logger.warning(
            "prompt files ignored (naming rule <name>_<date>_<version>): %s", ignored
        )

    if version is not None:
        want = _parse_version(version)
        matched = [pf for pf in matched if pf.version == want]

    if not matched:
        hint = f" (규칙에 맞지 않아 무시된 파일: {ignored})" if ignored else ""
        ver = f" version={version!r}" if version else ""
        raise FileNotFoundError(f"no prompt matches name={stem!r}{ver} in {directory}{hint}")

    matched.sort(key=lambda pf: pf.sort_key)
    best = matched[-1]

    # 날짜+버전이 같은 파일이 둘 이상이면 어느 것이 최신인지 알 수 없으므로 에러
    ties = [pf for pf in matched if pf.sort_key == best.sort_key]
    if len(ties) > 1:
        names = ", ".join(pf.path.name for pf in ties)
        raise ValueError(f"ambiguous prompt {stem!r}: {names}")

    return best


@lru_cache(maxsize=None)
def load_prompt(name: str, version: str | None = None) -> str:
    """프롬프트 파일을 읽어 문자열로 반환한다.

    load_prompt("agent_system")                  → 가장 최신 파일
    load_prompt("agent_system", version="1.1")   → 버전 고정 (그 버전 중 최신 날짜)
    load_prompt("agent_system_20261127_v1.md")   → 파일 직접 지정
    """
    pf = resolve_prompt(name, version)
    text = pf.path.read_text(encoding="utf-8-sig").strip()    # BOM 처리
    if not text:
        raise ValueError(f"prompt file is empty: {pf.path}")

    logger.info("prompt loaded: %s (date=%s, version=%s)", pf.path.name, pf.date, pf.version_str)
    return text