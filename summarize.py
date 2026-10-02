#!/usr/bin/env python3
"""청렴 신고 사건·교육 현황 CSV 자동 통계 요약 도구.

사용 예:
  python summarize.py --cases 청렴신고_사건데이터.csv --education 청렴교육_현황.csv
  python summarize.py --cases data/cases.csv --education data/education.csv --out reports

출력:
  summary_report.md : 사람이 읽기 쉬운 Markdown 요약
  summary.json      : 후속 자동화에 사용할 구조화 데이터
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import pandas as pd

def clean_num(s):
    return pd.to_numeric(s, errors="coerce")

def counts(df, col):
    return {str(k): int(v) for k, v in df[col].dropna().value_counts().items()}

def pct(v):
    return None if pd.isna(v) else round(float(v), 2)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", required=True, help="청렴 신고 사건 CSV")
    ap.add_argument("--education", required=True, help="청렴 교육 현황 CSV")
    ap.add_argument("--out", default="reports", help="출력 디렉터리")
    args = ap.parse_args()

    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    cases = pd.read_csv(args.cases, encoding="utf-8-sig")
    edu = pd.read_csv(args.education, encoding="utf-8-sig")

    cases["신고일자"] = pd.to_datetime(cases["신고일자"], errors="coerce")
    cases["처리기간_일"] = clean_num(cases["처리기간_일"])
    cases["위반금액_만원"] = clean_num(cases["위반금액_만원"])
    edu["교육이수율"] = clean_num(edu["교육이수율"])
    edu["연간교육시간"] = clean_num(edu["연간교육시간"])
    edu["교육참여자수"] = clean_num(edu["교육참여자수"])

    case_days = cases["처리기간_일"].dropna()
    violation = cases["위반금액_만원"].dropna()
    completion = edu["교육이수율"].dropna()

    summary = {
        "generated_at": pd.Timestamp.now().isoformat(),
        "cases": {
            "rows": int(len(cases)),
            "date_min": cases["신고일자"].min().strftime("%Y-%m-%d") if cases["신고일자"].notna().any() else None,
            "date_max": cases["신고일자"].max().strftime("%Y-%m-%d") if cases["신고일자"].notna().any() else None,
            "missing": {c: int(cases[c].isna().sum()) for c in cases.columns},
            "by_type": counts(cases, "신고유형"),
            "by_region": counts(cases, "지역"),
            "by_reporter": counts(cases, "신고자유형"),
            "by_status": counts(cases, "처리상태"),
            "by_action": counts(cases, "조치결과"),
            "processing_days": {
                "count": int(case_days.size), "mean": pct(case_days.mean()),
                "median": pct(case_days.median()), "min": pct(case_days.min()), "max": pct(case_days.max())
            },
            "violation_amount_만원": {
                "count": int(violation.size), "mean": pct(violation.mean()),
                "median": pct(violation.median()), "min": pct(violation.min()), "max": pct(violation.max())
            }
        },
        "education": {
            "rows": int(len(edu)),
            "missing": {c: int(edu[c].isna().sum()) for c in edu.columns},
            "by_type": counts(edu, "기관유형"),
            "excellent": counts(edu, "청렴우수기관"),
            "completion_rate": {
                "count": int(completion.size), "mean": pct(completion.mean()),
                "median": pct(completion.median()), "min": pct(completion.min()), "max": pct(completion.max())
            },
            "annual_hours_mean": pct(edu["연간교육시간"].mean()),
            "participants_total": int(edu["교육참여자수"].sum(skipna=True)),
            "participants_mean": pct(edu["교육참여자수"].mean())
        }
    }

    (out/"summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    def bullets(d):
        return "\n".join(f"- {k}: {v:,}" if isinstance(v, int) else f"- {k}: {v}" for k,v in d.items())

    md = f"""# 청렴 데이터 자동 통계 요약

생성시각: {summary["generated_at"]}

## 1. 청렴 신고 사건
- 전체 사건: **{summary["cases"]["rows"]:,}건**
- 신고일자 범위: **{summary["cases"]["date_min"]} ~ {summary["cases"]["date_max"]}**
- 평균 처리기간: **{summary["cases"]["processing_days"]["mean"]}일**
- 중앙값 처리기간: **{summary["cases"]["processing_days"]["median"]}일**
- 평균 위반금액: **{summary["cases"]["violation_amount_만원"]["mean"]:,}만원**
- 중앙값 위반금액: **{summary["cases"]["violation_amount_만원"]["median"]:,}만원**

### 신고유형
{bullets(summary["cases"]["by_type"])}

### 처리상태
{bullets(summary["cases"]["by_status"])}

### 지역
{bullets(summary["cases"]["by_region"])}

### 신고자유형
{bullets(summary["cases"]["by_reporter"])}

### 조치결과
{bullets(summary["cases"]["by_action"])}

## 2. 청렴 교육 현황
- 전체 기관: **{summary["education"]["rows"]:,}곳**
- 평균 교육이수율: **{summary["education"]["completion_rate"]["mean"]}%**
- 평균 연간교육시간: **{summary["education"]["annual_hours_mean"]}시간**
- 총 교육참여자수: **{summary["education"]["participants_total"]:,}명**
- 청렴우수기관 지정: **{summary["education"]["excellent"].get("Y", 0):,}곳**

### 기관유형
{bullets(summary["education"]["by_type"])}

### 청렴우수기관
{bullets(summary["education"]["excellent"])}

## 3. 결측치
사건 데이터:
{bullets(summary["cases"]["missing"])}

교육 데이터:
{bullets(summary["education"]["missing"])}

> 공개 서비스에 적용할 때는 개인정보·비공개 정보, 법적 공개근거, 데이터 갱신주기 및 원문 데이터의 정확성을 별도로 검토하세요.
"""
    (out/"summary_report.md").write_text(md, encoding="utf-8")
    print(f"완료: {out/'summary_report.md'}")
    print(f"완료: {out/'summary.json'}")

if __name__ == "__main__":
    main()
