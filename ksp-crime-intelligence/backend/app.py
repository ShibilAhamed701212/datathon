import os
import logging
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict

from . import database
from . import graph as graph_module
from . import rag_utils
from . import translator
from . import transcriber
from . import pdf_export

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="KSP Crime Intelligence Copilot API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str
    lang: str = "en"
    llm_mode: str = "mock"

class QueryResponse(BaseModel):
    answer: str
    source_ids: List[int] = []

@app.on_event("startup")
async def startup():
    logger.info("Initializing RAG index...")
    rag_utils.initialize_index()
    logger.info("RAG index initialized.")

@app.post("/api/query", response_model=QueryResponse)
def chat_query(data: QueryRequest):
    try:
        question = data.question
        if data.lang == "kn":
            question = translator.translate_to_english(question)

        context = rag_utils.retrieve_context(question)
        answer = rag_utils.generate_answer(question, context, llm_mode=data.llm_mode)
        source_ids = [d["fir_id"] for d in context]

        if data.lang == "kn":
            answer = translator.translate_to_kannada(answer)

        return QueryResponse(answer=answer, source_ids=source_ids)
    except Exception as e:
        logger.error(f"Query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class StatsResponse(BaseModel):
    crimes_by_type: List[Dict]
    crimes_by_district: List[Dict]
    crimes_by_month: List[Dict]
    repeat_offenders: List[Dict]

@app.get("/api/stats", response_model=StatsResponse)
def get_stats():
    try:
        return StatsResponse(
            crimes_by_type=database.get_stats_crimes_by_type(),
            crimes_by_district=database.get_stats_crimes_by_district(),
            crimes_by_month=database.get_stats_crimes_by_month(),
            repeat_offenders=database.get_stats_repeat_offenders(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats/crimes_by_type")
def stats_crimes_by_type():
    return database.get_stats_crimes_by_type()

@app.get("/api/stats/crimes_by_district")
def stats_crimes_by_district():
    return database.get_stats_crimes_by_district()

@app.get("/api/stats/crimes_by_month")
def stats_crimes_by_month():
    return database.get_stats_crimes_by_month()

@app.get("/api/stats/repeat_offenders")
def stats_repeat_offenders():
    return database.get_stats_repeat_offenders()

@app.get("/api/graph")
def get_graph(person: Optional[str] = None):
    try:
        if person:
            return graph_module.build_person_network(person)
        return graph_module.build_crime_graph()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/firs")
def get_firs(fir_id: Optional[int] = None, crime_type: Optional[str] = None,
             location: Optional[str] = None, district: Optional[str] = None,
             status: Optional[str] = None, limit: int = 50):
    try:
        return database.query_firs(fir_id=fir_id, crime_type=crime_type,
                                   location=location, district=district,
                                   status=status, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/firs/{fir_id}")
def get_fir_detail(fir_id: int):
    try:
        fir = database.query_firs(fir_id=fir_id)
        if not fir:
            raise HTTPException(status_code=404, detail="FIR not found")
        persons = database.query_involvements(fir_id=fir_id)
        return {"fir": fir[0], "persons": persons}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class SummaryRequest(BaseModel):
    fir_id: int

@app.post("/api/pdf_summary")
def pdf_summary(data: SummaryRequest):
    try:
        fir = database.query_firs(fir_id=data.fir_id)
        if not fir:
            raise HTTPException(status_code=404, detail="FIR not found")
        persons = database.query_involvements(fir_id=data.fir_id)
        pdf_buffer = pdf_export.generate_case_summary_pdf(fir[0], persons)
        from starlette.responses import StreamingResponse
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=fir_{data.fir_id}_summary.pdf"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        audio_bytes = await file.read()
        text = transcriber.transcribe_audio(audio_bytes)
        return {"text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ChatExportRequest(BaseModel):
    conversation: List[Dict]
    title: str = "Chat Export"

@app.post("/api/pdf_chat")
def pdf_chat_export(data: ChatExportRequest):
    try:
        pdf_buffer = pdf_export.generate_chat_pdf(data.conversation, data.title)
        from starlette.responses import StreamingResponse
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=chat_export.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "KSP Crime Intelligence Copilot"}
