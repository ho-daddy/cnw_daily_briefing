"""
AI 브리핑 생성 모듈
Claude API를 활용하여 수집된 데이터를 일일 동향 브리핑으로 변환
"""

import anthropic
import os
from datetime import datetime
from typing import Dict, List
import json


class BriefingGenerator:
    """AI 기반 브리핑 생성기"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-20250514"
    
    def format_data_for_prompt(self, data: Dict[str, List[Dict]]) -> str:
        """수집된 데이터를 프롬프트용 텍스트로 변환"""
        
        formatted_text = "# 오늘 수집된 노동안전보건 동향 자료\n\n"
        
        # 고용노동부 보도자료
        if data.get('moel_press'):
            formatted_text += "## 1. 고용노동부 보도자료\n"
            for item in data['moel_press']:
                formatted_text += f"- [{item['date']}] {item['title']}\n"
                formatted_text += f"  링크: {item['link']}\n\n"
        
        # 산업안전포털 공지사항
        if data.get('kosha_notice'):
            formatted_text += "## 2. 산업안전포털 공지사항\n"
            for item in data['kosha_notice']:
                formatted_text += f"- [{item['date']}] {item['title']}\n"
                formatted_text += f"  링크: {item['link']}\n\n"
        
        # 중대재해 발생알림
        if data.get('major_accident'):
            formatted_text += "## 3. 중대재해 발생알림\n"
            for item in data['major_accident']:
                formatted_text += f"- [{item['date']}] {item['title']}\n\n"
        
        # 매일노동뉴스
        if data.get('labor_news'):
            formatted_text += "## 4. 매일노동뉴스 안전과 건강\n"
            for item in data['labor_news']:
                formatted_text += f"- [{item['date']}] {item['title']}\n"
                formatted_text += f"  링크: {item['link']}\n\n"
        
        return formatted_text
    
    def generate_briefing(self, scraped_data: Dict[str, List[Dict]]) -> str:
        """수집된 데이터를 기반으로 브리핑 생성"""
        
        today = datetime.now().strftime("%Y년 %m월 %d일")
        data_text = self.format_data_for_prompt(scraped_data)
        
        prompt = f"""당신은 **산업안전보건 전문가**입니다. 다음 자료를 바탕으로 새움터(노동안전보건 민간단체) 실무자들을 위한 일일 동향 브리핑을 작성해주세요.

{data_text}

## 브리핑 작성 가이드

### 중점 사항 (매우 중요!)
- **산업안전보건**에 초점을 맞추세요
- 중대재해, 산업재해, 작업장 안전, 직업병 관련 내용을 우선 다루세요
- 일반 노동 이슈(임금, 고용, 복지 등)는 안전보건과 직접 연관된 경우만 간략히 언급
- 예방활동, 안전조치, 위험요인 관련 정보를 강조

### 구성
1. **핵심 요약** (3-4문장)
   - 오늘의 가장 중요한 안전보건 이슈
   - 중대재해나 긴급 안전 사항 우선

2. **주요 동향**
   - **중대재해 및 사고**: 발생 현황과 원인
   - **정책/제도**: 안전보건 관련 정부 정책, 법령 변화
   - **예방 및 대응**: 안전 캠페인, 점검, 교육 등
   - **기타 주목 사항**: 안전보건 관련 연구, 통계 등

3. **새움터 시사점** (2-3문장)
   - 새움터 활동에 참고할 만한 정보
   - 주의가 필요한 안전보건 현안

### 작성 원칙
- 명확하고 전문적인 톤 유지
- 불필요한 서론/결론 없이 핵심만 전달
- 각 항목에 출처 명시 (예: [고용노동부], [매일노동뉴스])
- 실무자가 5분 안에 파악할 수 있도록 간결하게

### 제외할 내용
- 일반 고용/임금 이슈 (안전보건 무관)
- 노사관계 일반론
- 정치적 논평

오늘 날짜: {today}
"""
        
        try:
            print("🤖 AI 브리핑 생성 중...")
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            briefing = response.content[0].text
            print("✅ 브리핑 생성 완료!")
            
            return briefing
            
        except Exception as e:
            print(f"❌ 브리핑 생성 실패: {e}")
            return None
    
    def save_briefing(self, briefing: str, output_path: str = None):
        """브리핑을 파일로 저장"""
        
        if output_path is None:
            today = datetime.now().strftime("%Y%m%d")
            output_path = f"briefing_{today}.md"
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(briefing)
            print(f"💾 브리핑 저장 완료: {output_path}")
            return output_path
        except Exception as e:
            print(f"❌ 파일 저장 실패: {e}")
            return None
    
    def generate_and_save(self, scraped_data: Dict[str, List[Dict]], 
                         output_path: str = None) -> str:
        """브리핑 생성 및 저장을 한 번에 실행"""
        
        briefing = self.generate_briefing(scraped_data)
        
        if briefing:
            saved_path = self.save_briefing(briefing, output_path)
            return briefing, saved_path
        
        return None, None


if __name__ == "__main__":
    # 테스트용 샘플 데이터
    sample_data = {
        'moel_press': [
            {
                'title': "'추락안전매트'로 노동자의 안전을 지원",
                'date': '2026.01.28',
                'link': 'https://example.com/1',
                'source': '고용노동부'
            }
        ],
        'kosha_notice': [],
        'major_accident': [],
        'labor_news': []
    }
    
    # API 키 설정 필요
    generator = BriefingGenerator()
    # briefing, path = generator.generate_and_save(sample_data)
