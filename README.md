# fastMCP-playground
> FastMCP를 활용한 MCP(Model Context Protocol) 서버 개발 플레이그라운드

## 🧑‍💻: Intro
❓ Problem : LLM에 커스텀 도구(Tool)를 연결하는 MCP 서버를 빠르게 프로토타이핑할 방법이 필요함 😮

❗ Idea : FastMCP 프레임워크로 Python 데코레이터 방식의 간결한 Tool 정의를 채택 🤔

💯 Solution : `@mcp.tool()` 데코레이터 하나로 MCP 호환 도구를 즉시 등록·실행 😁

</br>

## 🖥️: API Documentation
[Swagger UI](https://hyeonwoody.com/swagger/?urls.primaryName=fastMCP)

</br>

## 🧱: Structure

```
fastMCP/
├── hello_mcp.py      # MCP 서버 진입점 및 예시 Tool 정의
├── pyproject.toml    # 프로젝트 메타데이터 및 의존성
└── uv.lock           # 의존성 잠금 파일
```

</br>

## 🛢️: Entity Relationship Diagram

</br>

## 🚀: Build & Run

### Prerequisites
- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager

### Initialization

```bash
# 의존성 설치
uv sync
```

### Run

```bash
# MCP 서버 실행 (stdio transport)
uv run python hello_mcp.py

# 또는 fastmcp CLI 사용
uv run fastmcp run hello_mcp.py
```

### Development (SSE/HTTP transport)

```bash
uv run fastmcp dev inspector hello_mcp.py
```

</br>

## 🗓️: Development Period

2026.06.11 ~

<br>

## 🔥: Accomplishments

- FastMCP 기반 MCP 서버 기본 구조 구축
- `greet` Tool 등록 및 동작 확인

<br>

## ✅: Implementation

- [x] FastMCP 서버 초기화
- [x] `greet(name)` Tool 구현

<br>

## 📓: Log

### 2026.06.11
Initial FastMCP playground setup with greet tool.

<br>

## 🎥: Demonstration

</br>

## 🎨: Design

</br>

## 📞: Contact
- 이메일: hyeonwoody@gmail.com
- 블로그: https://velog.io/@hyeonwoody
- 깃헙: https://github.com/hyeonwoody

</br>

## 🛠️: Technologies Used
> Python 3.10+, FastMCP, FastAPI

</br>

## 📚: Libraries Used
> fastmcp >= 0.1.0, fastapi >= 0.136.3

## 📖: Wiki
