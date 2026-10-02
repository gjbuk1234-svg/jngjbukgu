# 청렴 신고 정적 검색·필터 페이지

## 구현 항목
- `<title>`: `청렴 신고 사건 검색·조회`
- 제공 CSV 500건을 `data/cases.json`으로 변환
- 사건 카드에 **신고일자 / 신고유형 / 지역 / 처리상태** 표시
- **신고유형 / 처리상태 / 사건ID** 필터
- 화면에 `결과 N건` 표시
- 행정안전부 RSS 출처 링크: https://www.korea.kr/rss/dept_mois.xml
- `build_rss.py`가 배포 빌드 시 RSS를 조회해 최신 5건 이상을 `data/mois-rss.json`에 정적으로 생성
- RSS 서버가 일시적으로 응답하지 않을 때 재현 가능한 체크인 스냅샷으로 빌드 가능
- Netlify / Vercel 설정 파일 포함

## Netlify
GitHub 저장소에 이 폴더를 올린 뒤 Netlify에서 저장소를 연결하면 `netlify.toml`의 빌드 설정을 사용합니다.
Build command: `python3 build_rss.py`
Publish directory: `.`

## Vercel
저장소를 Vercel에 연결하면 `vercel.json`의 build command를 사용합니다.

> 이 실행 환경에서는 사용자의 Netlify/Vercel 계정 인증정보가 없으므로 외부 계정에 실제 사이트를 대신 배포할 수는 없습니다. 대신 바로 연결 가능한 배포 산출물과 빌드 설정을 구성했습니다.

## 로컬 확인
Python이 있다면:
```bash
python3 -m http.server 8000
```
브라우저에서 `http://localhost:8000` 접속.

## RSS 관련 확인
행정안전부는 RSS 서비스를 제공한다고 안내하고 있습니다. 실제 배포 빌드에서는 지정된 `korea.kr` RSS URL을 우선 조회합니다.
