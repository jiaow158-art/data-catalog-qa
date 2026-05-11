import time
from fastapi import APIRouter
from sqlalchemy.orm import Session

from app.api.deps import DBSession
from app.schemas.qa import QaRequest, QaResponse, LLMConfigResponse, LLMConfigUpdate, LLMTestResponse, LLMTestRequest
from app.services import qa_service
from app.core.config import settings
from app.core.llm_config import get_llm_config, set_llm_config, clear_llm_config

router = APIRouter(prefix="/qa", tags=["智能问答"])


@router.post("/ask", response_model=QaResponse)
def ask(req: QaRequest, db: Session = DBSession):
    result = qa_service.ask(db, req.question, use_llm=req.use_llm)
    return QaResponse(**result)


@router.get("/config", response_model=LLMConfigResponse)
def get_config():
    """Get current LLM configuration with API key masked."""
    runtime = get_llm_config()
    return LLMConfigResponse(
        provider=settings.LLM_PROVIDER,
        model=runtime.get("model") or settings.LLM_MODEL,
        base_url=runtime.get("base_url") or settings.LLM_BASE_URL,
        api_key_configured=bool(runtime.get("api_key") or settings.LLM_API_KEY),
        max_tokens=settings.LLM_MAX_TOKENS,
        temperature=settings.LLM_TEMPERATURE,
    )


@router.put("/config")
def update_config(data: LLMConfigUpdate):
    """Update LLM configuration at runtime. Changes take effect immediately."""
    set_llm_config({k: v for k, v in data.model_dump().items() if v is not None})
    return {"ok": True}


@router.post("/config/test", response_model=LLMTestResponse)
def test_config(data: LLMTestRequest = LLMTestRequest()):
    """Test the LLM connection. Uses provided values if given, otherwise falls back to current config."""
    runtime = get_llm_config()
    api_key = data.api_key or runtime.get("api_key") or settings.LLM_API_KEY
    base_url = data.base_url or runtime.get("base_url") or settings.LLM_BASE_URL or None
    model = data.model or runtime.get("model") or settings.LLM_MODEL

    if not api_key or api_key == "sk-xxx":
        return LLMTestResponse(ok=False, message="API Key 未配置，请在设置中填写有效的 API Key")

    try:
        from openai import OpenAI
    except ImportError:
        return LLMTestResponse(ok=False, message="openai 库未安装")

    kwargs = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url
    client = OpenAI(**kwargs)

    t0 = time.time()
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=16,
            temperature=0,
        )
        latency = int((time.time() - t0) * 1000)
        reply = response.choices[0].message.content or ""
        return LLMTestResponse(
            ok=True,
            message=f"连接成功！模型回复: {reply}",
            model=model,
            latency_ms=latency,
        )
    except Exception as e:
        latency = int((time.time() - t0) * 1000)
        err = str(e)
        return LLMTestResponse(
            ok=False,
            message=f"连接失败: {err}",
            model=model,
            latency_ms=latency,
        )

