# Synapster (fastMCP)
> FastAPI에 FastMCP를 마운트한 RAG 기반 문서 검색·질의응답 MCP(Model Context Protocol) 서버

## 🧑‍💻: Intro
❓ Problem : LLM에 프로젝트 문서/README/Q&A를 컨텍스트로 연결하면서, 매 질의마다 임베딩·검색·생성을 반복하면 응답 지연이 커짐 😮

❗ Idea : FastMCP의 `@mcp.tool()` 데코레이터로 도구를 간결하게 정의하고, 하이브리드 검색 + 리랭킹 + 시맨틱 캐시로 검색 품질과 RTT를 동시에 잡자 🤔

💯 Solution : FastAPI에 FastMCP를 `/mcp`로 마운트하고, BGE-M3 임베딩 → 하이브리드 검색 → Cross-encoder 리랭킹 → LLM 생성 파이프라인을 구성. 시맨틱 캐시 적중 시 LLM 호출을 우회해 end-to-end RTT 감소 😁

</br>

## 🧱: Structure

```
fastMCP/
├── app/
│   ├── main.py            # FastAPI 진입점, FastMCP를 /mcp로 마운트
│   ├── state.py           # FastMCP 인스턴스 및 Ports(어댑터) 조립
│   ├── lang_serve.py      # LangServe 대체 엔트리 포인트
│   └── routes/            # mcp / projects / utils 라우터
├── tools/                 # @mcp.tool() — greet, ask_question(RAG 질의)
├── pipelines/             # ingestion · retrieval · sync · chunking · cleaning · embedding · indexing
├── services/
│   ├── embedding.py       # BGE-M3 (dense + sparse) 임베딩
│   ├── reranker.py        # BGE-reranker-v2-m3 Cross-encoder
│   ├── cache.py           # Qdrant 기반 시맨틱 캐시
│   ├── llm/               # 교체 가능한 LLM 어댑터 (ollama · openAI · mistral · qwen)
│   └── store/             # 벡터 스토어 어댑터 (qdrant · chroma)
├── config/settings.py     # pydantic-settings (env_prefix: SYNAPSTER_)
├── models/                # 도메인 모델 및 Pydantic 스키마
├── pyproject.toml         # 프로젝트 메타데이터 및 의존성
└── uv.lock                # 의존성 잠금 파일
```

</br>

## 🛠️: Architecture

- **Port/Adapter 패턴**: `services/ports.py`의 Protocol 인터페이스로 임베딩·스토어·리랭커·LLM·캐시를 추상화 → 구현체 교체 시 파이프라인/도구 수정 불필요
- **Hybrid Retrieval**: BGE-M3 dense + sparse 벡터를 Qdrant에서 동시 검색
- **Reranking**: BGE-reranker-v2-m3 Cross-encoder로 후보 재정렬
- **Semantic Cache**: 질의 임베딩 코사인 유사도(기본 0.92) 적중 시 캐시된 답변 즉시 반환

### Endpoints

| Method | Path | 설명 |
|--------|------|------|
| `*` | `/mcp` | FastMCP 엔드포인트 (도구: `greet`, `ask_question`) |
| `POST` | `/projects/{project_id}/readme/sync` | 프로젝트 README 동기화 → 임베딩·색인 |
| `POST` | `/utils/greet` | 헬스 체크용 유틸 |
| `GET` | `/health` | 서버 상태 |

</br>

## 🚀: Build & Run

### Prerequisites
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- [Qdrant](https://qdrant.tech/) (벡터 스토어 / 시맨틱 캐시)
- [Ollama](https://ollama.com/) (기본 LLM 어댑터, `EEVE-Korean-Instruct-10.8B`)

### Initialization

```bash
# 의존성 설치
uv sync

# 환경 변수 설정 (.env)
cp .env.example .env   # SYNAPSTER_* 값 조정
```

### Run

```bash
# Synapster 서버 실행 (FastAPI + FastMCP, HTTP)
uv run server          # == uvicorn app.main:api

# 또는 직접 실행
uv run python -m app.main

# LangServe 엔트리 포인트
uv run langserve
```

기본 포트는 `8000` (`SYNAPSTER_PORT`로 변경). MCP 엔드포인트는 `http://localhost:8000/mcp`.

</br>

## 🗓️: Development Period

2026.06.11 ~

<br>

## 🔥: Accomplishments

- FastAPI + FastMCP 마운트 구조로 MCP 도구와 REST 라우터 공존
- BGE-M3 하이브리드 검색 + Cross-encoder 리랭킹 검색 파이프라인 구축
- Qdrant 기반 시맨틱 캐시로 반복 질의 RTT 단축
- Port/Adapter 패턴으로 LLM·벡터스토어 프로바이더 교체 가능하게 분리
- 문서/Q&A 인제스션 파이프라인 (clean → chunk → embed → index) 구현

<br>

## ✅: Implementation

- [x] FastMCP 서버 초기화 및 FastAPI 마운트
- [x] `greet(name)` Tool 구현
- [x] `ask_question` RAG 질의 Tool 구현
- [x] BGE-M3 임베딩 / BGE-reranker 리랭킹 서비스
- [x] Qdrant 벡터 스토어 및 시맨틱 캐시
- [x] 문서 / Q&A 인제스션 파이프라인
- [x] 프로젝트 README 동기화 라우트
- [ ] 세션 히스토리 / 멀티턴 대화
- [ ] 테스트 및 문서화

<br>

## 📓: Log

### 2026.06.11
Initial FastMCP playground setup with greet tool.

### 2026.06
RAG 파이프라인(인제스션·검색·리랭킹·시맨틱 캐시) 및 FastAPI 마운트로 Synapster 서버 구축.

<br>

## 📞: Contact
- 이메일: hyeonwoody@gmail.com
- 블로그: https://velog.io/@hyeonwoody
- 깃헙: https://github.com/hyeonwoody

</br>

## 🛠️: Technologies Used
> Python 3.11+
> FastAPI
> FastMCP
> Qdrant
> Ollama

</br>

## 📚: Libraries Used
> fastapi >= 0.136.3
> fastmcp >= 2
> qdrant-client >= 1.9
> sentence-transformers >= 3.0
> FlagEmbedding >= 1.4
> langchain-ollama >= 0.3
> structlog

## 📖: Wiki
