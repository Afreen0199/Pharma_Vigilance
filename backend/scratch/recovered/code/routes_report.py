from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from app.services.report_service import report_service_instance
from app.services.database_service import db_service
from app.services.fda_service import fda_service_instance
from app.services.regulatory_service import regulatory_service_instance
from app.services.rag_service import rag_service_instance
from app.services.llm_service import llm_service_instance
from typing import Optional
import os
import json
import logging

from app.services.verification.evidence_service import evidence_service
from app.services.verification.reasoning_service import reasoning_service

logger = logging.getLogger(__name__)

def normalize_report_data(report_data: dict, ocr_metadata: Optional[dict] = None) -> dict:
# If it is a parent multi-case report, skip single-case schema normalization
if "cases" in report_data and isinstance(report_data["cases"], list):
return report_data

# Ensure all required sections exist in the JSON
for section in [
"patient_demographic", "patient_information", "patient_details",
"drug_information", "adverse_events",
"drug_batch_details", "therapy_information", "reporter_information"
]:
if section not in report_data or not isinstance(report_data[section], dict):
report_data[section] = {}

p_demo = report_data["patient_demographic"]
p_info = rep
# MISSING LINE 36
# MISSING LINE 37
# MISSING LINE 38
# MISSING LINE 39
# MISSING LINE 40
# MISSING LINE 41
# MISSING LINE 42
# MISSING LINE 43
# MISSING LINE 44
# MISSING LINE 45
# MISSING LINE 46
# MISSING LINE 47
# MISSING LINE 48
# MISSING LINE 49
# MISSING LINE 50
# MISSING LINE 51
# MISSING LINE 52
# MISSING LINE 53
# MISSING LINE 54
# MISSING LINE 55
# MISSING LINE 56
# MISSING LINE 57
# MISSING LINE 58
# MISSING LINE 59
# MISSING LINE 60
# MISSING LINE 61
# MISSING LINE 62
# MISSING LINE 63
# MISSING LINE 64
# MISSING LINE 65
# MISSING LINE 66
# MISSING LINE 67
# MISSING LINE 68
# MISSING LINE 69
# MISSING LINE 70
# MISSING LINE 71
# MISSING LINE 72
# MISSING LINE 73
# MISSING LINE 74
# MISSING LINE 75
# MISSING LINE 76
# MISSING LINE 77
# MISSING LINE 78
# MISSING LINE 79
# MISSING LINE 80
# MISSING LINE 81
# MISSING LINE 82
# MISSING LINE 83
# MISSING LINE 84
# MISSING LINE 85
# MISSING LINE 86
# MISSING LINE 87
# MISSING LINE 88
# MISSING LINE 89
# MISSING LINE 90
# MISSING LINE 91
# MISSING LINE 92
# MISSING LINE 93
# MISSING LINE 94
# MISSING LINE 95
# MISSING LINE 96
# MISSING LINE 97
# MISSING LINE 98
# MISSING LINE 99
# MISSING LINE 100
# MISSING LINE 101
# MISSING LINE 102
# MISSING LINE 103
# MISSING LINE 104
# MISSING LINE 105
# MISSING LINE 106
# MISSING LINE 107
# MISSING LINE 108
# MISSING LINE 109
# MISSING LINE 110
# MISSING LINE 111
# MISSING LINE 112
# MISSING LINE 113
# MISSING LINE 114
# MISSING LINE 115
# MISSING LINE 116
# MISSING LINE 117
# MISSING LINE 118
# MISSING LINE 119
# MISSING LINE 120
# MISSING LINE 121
# MISSING LINE 122
# MISSING LINE 123
# MISSING LINE 124
# MISSING LINE 125
# MISSING LINE 126
# MISSING LINE 127
# MISSING LINE 128
# MISSING LINE 129
# MISSING LINE 130
# MISSING LINE 131
# MISSING LINE 132
# MISSING LINE 133
# MISSING LINE 134
# MISSING LINE 135
# MISSING LINE 136
# MISSING LINE 137
# MISSING LINE 138
# MISSING LINE 139
# MISSING LINE 140
# MISSING LINE 141
# MISSING LINE 142
# MISSING LINE 143
# MISSING LINE 144
# MISSING LINE 145
# MISSING LINE 146
# MISSING LINE 147
# MISSING LINE 148
# MISSING LINE 149
# MISSING LINE 150
# MISSING LINE 151
# MISSING LINE 152
# MISSING LINE 153
# MISSING LINE 154
# MISSING LINE 155
# MISSING LINE 156
# MISSING LINE 157
# MISSING LINE 158
# MISSING LINE 159
# MISSING LINE 160
# MISSING LINE 161
# MISSING LINE 162
# MISSING LINE 163
# MISSING LINE 164
# MISSING LINE 165
# MISSING LINE 166
# MISSING LINE 167
# MISSING LINE 168
# MISSING LINE 169
# MISSING LINE 170
# MISSING LINE 171
# MISSING LINE 172
# MISSING LINE 173
# MISSING LINE 174
# MISSING LINE 175
# MISSING LINE 176
# MISSING LINE 177
# MISSING LINE 178
# MISSING LINE 179
# MISSING LINE 180
# MISSING LINE 181
# MISSING LINE 182
# MISSING LINE 183
# MISSING LINE 184
# MISSING LINE 185
# MISSING LINE 186
# MISSING LINE 187
# MISSING LINE 188
# MISSING LINE 189
# MISSING LINE 190
# MISSING LINE 191
# MISSING LINE 192
# MISSING LINE 193
# MISSING LINE 194
# MISSING LINE 195
# MISSING LINE 196
# MISSING LINE 197
# MISSING LINE 198
# MISSING LINE 199
# MISSING LINE 200
# MISSING LINE 201
# MISSING LINE 202
# MISSING LINE 203
# MISSING LINE 204
# MISSING LINE 205
# MISSING LINE 206
# MISSING LINE 207
# MISSING LINE 208
# MISSING LINE 209
# MISSING LINE 210
# MISSING LINE 211
# MISSING LINE 212
# MISSING LINE 213
# MISSING LINE 214
# MISSING LINE 215
# MISSING LINE 216
# MISSING LINE 217
# MISSING LINE 218
# MISSING LINE 219
# MISSING LINE 220
# MISSING LINE 221
# MISSING LINE 222
# MISSING LINE 223
# MISSING LINE 224
# MISSING LINE 225
# MISSING LINE 226
# MISSING LINE 227
# MISSING LINE 228
# MISSING LINE 229
# MISSING LINE 230
# MISSING LINE 231
# MISSING LINE 232
# MISSING LINE 233
# MISSING LINE 234

ai_summary_text = case_data.get("ai_summary", "")
try:
report_data = json.loads(ai_summary_text)

# Normalize report data on the fly to ensure consistent schema and missing fields formatting
report_data = normalize_report_data(report_data, report_data.get("ocr_metadata"))

response_data = report_data.copy()
response_data["report_id"] = analysis_id
response_data["json_url"] = f"/report/download/{analysis_id}?format=json"
response_data["excel_url"] = f"/report/download/{analysis_id}?format=xlsx"
response_data["pdf_url"] = f"/report/download/{analysis_id}?format=pdf"
response_data["status"] = "success"
response_data["cached"] = True

# Regenerate on-disk files if missing
report_service_instance.generate_json_report(report_data, analysis_id)
report_service_instance.generate_excel_report(report_data, analysis_id)
report_service_instance.generate_pdf_report(report_data, analysis_id)

return response_data
except Exception:
# Fallback to older format structure
fda_signals_data = case_data.get("fda_signals", {})
visualizations_data = {}
# MISSING LINE 261
# MISSING LINE 262
# MISSING LINE 263
# MISSING LINE 264
# MISSING LINE 265
# MISSING LINE 266
# MISSING LINE 267
# MISSING LINE 268
# MISSING LINE 269
# MISSING LINE 270
# MISSING LINE 271
# MISSING LINE 272
# MISSING LINE 273
# MISSING LINE 274
# MISSING LINE 275
# MISSING LINE 276
# MISSING LINE 277
# MISSING LINE 278
# MISSING LINE 279
# MISSING LINE 280
# MISSING LINE 281
# MISSING LINE 282
# MISSING LINE 283
# MISSING LINE 284
# MISSING LINE 285
# MISSING LINE 286
# MISSING LINE 287
# MISSING LINE 288
# MISSING LINE 289
report_service_instance.generate_pdf_report(report_data, analysis_id)
except Exception as e:
logger.warning(f"Error compiling downloadable files for cached report: {e}")

res_dict = {
"report_id": analysis_id,
"json_url": f"/report/download/{analysis_id}?format=json",
"excel_url": f"/report/download/{analysis_id}?format=xlsx",
"pdf_url": f"/report/download/{analysis_id}?format=pdf",
"status": "success",
"cached": True,
"drug_entities": case_data.get("drugs", []),
"symptoms": case_data.get("symptoms", []),
"regulatory_alerts": case_data.get("regulatory_alerts", []),
"fda_signal": fda_signals_data,
"visualizations": visualizations_data,
"summary": ai_summary_text,
"seriousness_assessment": case_data.get("seriousness_assessment", {}),
"causality_assessment": case_data.get("causality_assessment", {}),
"timeline": case_data.get("timeline", []),
"missing_data": case_data.get("missing_data", [])
}
if ocr_metadata:
res_dict["ocr_metadata"] = ocr_metadata
return res_dict
# 2.5. Check if it is a multi-case parent document
is_parent = False
# MISSING LINE 317
# MISSING LINE 318
# MISSING LINE 319
# MISSING LINE 320
# MISSING LINE 321
# MISSING LINE 322
# MISSING LINE 323
# MISSING LINE 324
# MISSING LINE 325
# MISSING LINE 326
# MISSING LINE 327
# MISSING LINE 328
# MISSING LINE 329
# MISSING LINE 330
# MISSING LINE 331
# MISSING LINE 332
# MISSING LINE 333
# MISSING LINE 334
# MISSING LINE 335
# MISSING LINE 336
# MISSING LINE 337
# MISSING LINE 338
# MISSING LINE 339
# MISSING LINE 340
# MISSING LINE 341
# MISSING LINE 342
# MISSING LINE 343
# MISSING LINE 344
# MISSING LINE 345
# MISSING LINE 346
# MISSING LINE 347
# MISSING LINE 348
# MISSING LINE 349
# MISSING LINE 350
# MISSING LINE 351
# MISSING LINE 352
# MISSING LINE 353
# MISSING LINE 354
# MISSING LINE 355
# MISSING LINE 356
# MISSING LINE 357
# MISSING LINE 358
# MISSING LINE 359
# MISSING LINE 360
# MISSING LINE 361
# MISSING LINE 362
# MISSING LINE 363
# MISSING LINE 364
# MISSING LINE 365
# MISSING LINE 366
# MISSING LINE 367
# MISSING LINE 368
# MISSING LINE 369
# MISSING LINE 370
# MISSING LINE 371
# MISSING LINE 372
# MISSING LINE 373
# MISSING LINE 374

parent_report_data = {
"total_cases_detected": len(child_ids),
"cases": cases_payload,
"bundle_url": f"/report/download/{analysis_id}?format=zip",
"status": "success",
"cached": False,
"report_id": analysis_id
}

# Save parent completed state to Supabase
db_service.update_case_analysis_results(
analysis_id=analysis_id,
ai_summary=json.dumps(parent_report_data),
seriousness_assessment={},
causality_assessment={},
timeline=[],
missing_data=[],
regulatory_alerts=[],
fda_signals={}
)

# Write parent JSON and Excel downloads on disk
report_service_instance.generate_json_report(parent_report_data, analysis_id)
report_service_instance.generate_excel_report(parent_report_data, analysis_id)

return parent_report_data
except Exception as e:
logger.error(f"Failed to generate parent multi-case report '{analysis_id}': {e}")
raise HTTPException(status_code=500, detail=f"Failed to process multi-case report: {e}")

# MISSING LINE 406
# MISSING LINE 407
# MISSING LINE 408
# MISSING LINE 409
# MISSING LINE 410
# MISSING LINE 411
# MISSING LINE 412
# MISSING LINE 413
# MISSING LINE 414
# MISSING LINE 415
# MISSING LINE 416
# MISSING LINE 417
# MISSING LINE 418
# MISSING LINE 419
# MISSING LINE 420
# MISSING LINE 421
# MISSING LINE 422
# MISSING LINE 423
# MISSING LINE 424
# MISSING LINE 425
# MISSING LINE 426
# MISSING LINE 427
# MISSING LINE 428
# MISSING LINE 429
# MISSING LINE 430
# MISSING LINE 431
# MISSING LINE 432
# MISSING LINE 433
# MISSING LINE 434
# MISSING LINE 435
# MISSING LINE 436
# MISSING LINE 437
# MISSING LINE 438
# MISSING LINE 439
# MISSING LINE 440
# MISSING LINE 441
# MISSING LINE 442
# MISSING LINE 443
# MISSING LINE 444
# MISSING LINE 445
# MISSING LINE 446
# MISSING LINE 447
# MISSING LINE 448
# MISSING LINE 449
# MISSING LINE 450
# MISSING LINE 451
# MISSING LINE 452
# MISSING LINE 453
# MISSING LINE 454
# MISSING LINE 455
# MISSING LINE 456
# MISSING LINE 457
# MISSING LINE 458
# MISSING LINE 459
# MISSING LINE 460
# MISSING LINE 461
# MISSING LINE 462
# MISSING LINE 463
# MISSING LINE 464
# MISSING LINE 465
# MISSING LINE 466
# MISSING LINE 467
# MISSING LINE 468
# MISSING LINE 469
# MISSING LINE 470
# MISSING LINE 471
# MISSING LINE 472
# MISSING LINE 473
# MISSING LINE 474
# MISSING LINE 475
# MISSING LINE 476
# MISSING LINE 477
# MISSING LINE 478
# MISSING LINE 479
# MISSING LINE 480
# MISSING LINE 481
# MISSING LINE 482
# MISSING LINE 483
# MISSING LINE 484
# MISSING LINE 485
# MISSING LINE 486
# MISSING LINE 487
# MISSING LINE 488
# MISSING LINE 489
# MISSING LINE 490
# MISSING LINE 491
# MISSING LINE 492
# MISSING LINE 493
# MISSING LINE 494
# MISSING LINE 495
# MISSING LINE 496
# MISSING LINE 497
# MISSING LINE 498
# MISSING LINE 499
# MISSING LINE 500
# MISSING LINE 501
# MISSING LINE 502
# MISSING LINE 503
# MISSING LINE 504
# MISSING LINE 505
# MISSING LINE 506
# MISSING LINE 507
# MISSING LINE 508
# MISSING LINE 509
# MISSING LINE 510
# MISSING LINE 511
# MISSING LINE 512
# MISSING LINE 513
# MISSING LINE 514
# MISSING LINE 515
# MISSING LINE 516
# MISSING LINE 517
# MISSING LINE 518
# MISSING LINE 519
# MISSING LINE 520
# MISSING LINE 521
# MISSING LINE 522
# MISSING LINE 523
# MISSING LINE 524
# MISSING LINE 525
# MISSING LINE 526
# MISSING LINE 527
# MISSING LINE 528
# MISSING LINE 529
# MISSING LINE 530
# MISSING LINE 531
# MISSING LINE 532
# MISSING LINE 533
# MISSING LINE 534
# MISSING LINE 535
# MISSING LINE 536
# MISSING LINE 537
# MISSING LINE 538
# MISSING LINE 539
# MISSING LINE 540
# MISSING LINE 541
# MISSING LINE 542
# MISSING LINE 543
# MISSING LINE 544
# MISSING LINE 545
# MISSING LINE 546
# MISSING LINE 547
# MISSING LINE 548
# MISSING LINE 549
# MISSING LINE 550
# MISSING LINE 551
# MISSING LINE 552
# MISSING LINE 553
# MISSING LINE 554
# MISSING LINE 555
# MISSING LINE 556
# MISSING LINE 557
# MISSING LINE 558
# MISSING LINE 559
# MISSING LINE 560
# MISSING LINE 561
# MISSING LINE 562
# MISSING LINE 563
# MISSING LINE 564
# MISSING LINE 565
# MISSING LINE 566
# MISSING LINE 567
# MISSING LINE 568
# MISSING LINE 569
)

# G. Generate downloadable files on disk
report_service_instance.generate_json_report(report_data, analysis_id)
report_service_instance.generate_excel_report(report_data, analysis_id)
report_service_instance.generate_pdf_report(report_data, analysis_id)

# Format API response data
response_data = report_data.copy()
response_data["report_id"] = analysis_id
response_data["json_url"] = f"/report/download/{analysis_id}?format=json"
response_data["excel_url"] = f"/report/download/{analysis_id}?format=xlsx"
response_data["pdf_url"] = f"/report/download/{analysis_id}?format=pdf"
response_data["status"] = "success"
response_data["cached"] = False

return response_data

except Exception as e:
logger.error(f"Error during report generation: {e}")
raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{analysis_id}")
async def get_report_status(analysis_id: str):
"""
Checks the status of report generation for a given analysis_id.
"""
case_data = db_service.get_case_analysis(analysis_id)
if not case_data:
raise HTTPException(status_code=404, detail="Analysis ID not found.")

return {
"analysis_id": analysis_id,
"status": case_data.get("status"),
"created_at": case_data.get("created_at")
}

@router.get("/download/{report_id}")
async def download_report(report_id: str, format: str = "json"):
from app.services.report_service import REPORTS_DIR

filepath = os.path.join(REPORTS_DIR, f"{report_id}.{format}")
if not os.path.exists(filepath):
raise HTTPException(status_code=404, detail="Report file not found.")

return FileResponse(filepath, filename=f"report_{report_id}.{format}")

