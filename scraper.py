"""
노동안전보건 일일 동향 브리핑 시스템
데이터 수집 모듈
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict
import time
import os
import subprocess

# Playwright는 선택적으로 import
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
    
    # Streamlit Cloud에서 자동으로 브라우저 설치
    if not os.path.exists(os.path.expanduser("~/.cache/ms-playwright")):
        print("🔄 Playwright 브라우저 설치 중...")
        try:
            subprocess.run(["playwright", "install", "chromium", "--with-deps"], 
                         check=True, capture_output=True)
            print("✅ Playwright 브라우저 설치 완료")
        except Exception as e:
            print(f"⚠️ Playwright 브라우저 설치 실패: {e}")
            PLAYWRIGHT_AVAILABLE = False
            
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️ Playwright가 설치되지 않았습니다. 일부 사이트 수집이 제한됩니다.")


class SafetyNewsScraper:
    """노동안전보건 관련 뉴스 스크래퍼"""
    
    def __init__(self):
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.results = {
            'moel_press': [],          # 고용노동부 보도자료
            'kosha_notice': [],        # 산업안전포털 공지사항
            'major_accident': [],      # 중대재해 발생알림
            'labor_news': [],          # 매일노동뉴스
            'bigkinds_news': []        # Bigkinds 뉴스 검색
        }
    
    def scrape_moel_press_release(self):
        """고용노동부 보도자료 수집"""
        print("📄 고용노동부 보도자료 수집 중...")
        url = "https://www.moel.go.kr/news/enews/report/enewsList.do"
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, timeout=30, headers=headers)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 테이블에서 최근 게시물 추출
            table = soup.find('table')
            if not table:
                print("  ⚠️ 테이블을 찾을 수 없습니다")
                return
            
            rows = table.find_all('tr')[1:]  # 헤더 제외
            
            for row in rows[:15]:  # 최근 15개 체크
                try:
                    cols = row.find_all('td')
                    if len(cols) < 4:
                        continue
                    
                    # 제목 열 찾기 (보통 2번째 td)
                    title_col = None
                    for col in cols:
                        link_tag = col.find('a')
                        if link_tag:
                            title_col = col
                            break
                    
                    if not title_col:
                        continue
                    
                    link_tag = title_col.find('a')
                    title = link_tag.get_text(strip=True)
                    href = link_tag.get('href', '')
                    
                    # 링크 처리
                    if href.startswith('http'):
                        link = href
                    else:
                        link = "https://www.moel.go.kr/news/enews/report/" + href
                    
                    # 날짜 추출 (마지막에서 2번째 열)
                    date = cols[-2].get_text(strip=True) if len(cols) >= 2 else ''
                    
                    # 안전보건 관련 키워드 필터링
                    keywords = ['안전', '산재', '중대재해', '보건', '재해', '사고', '위험', '근로', '노동']
                    if any(keyword in title for keyword in keywords):
                        self.results['moel_press'].append({
                            'title': title,
                            'date': date,
                            'link': link,
                            'source': '고용노동부'
                        })
                except Exception as e:
                    continue
            
            print(f"  ✅ {len(self.results['moel_press'])}건 수집 완료")
            
        except Exception as e:
            print(f"  ❌ 수집 실패: {e}")
    
    def scrape_kosha_with_playwright(self):
        """산업안전포털 공지사항 수집 (Playwright 사용)"""
        print("📄 산업안전포털 공지사항 수집 중...")
        
        if not PLAYWRIGHT_AVAILABLE:
            print("  ⚠️ Playwright 미설치 - 건너뜀 (requests 방식으로 시도)")
            self.scrape_kosha_with_requests()
            return
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                page = context.new_page()
                
                # 타임아웃 짧게 설정 (20초)
                page.set_default_timeout(20000)
                
                print("  → 페이지 로딩 중...")
                try:
                    page.goto("https://portal.kosha.or.kr/community/notice", 
                             wait_until='domcontentloaded', timeout=15000)
                except:
                    print("  ⚠️ 페이지 로딩 시간 초과 - 건너뜀")
                    browser.close()
                    return
                
                # 테이블 대기 (짧은 시간)
                try:
                    page.wait_for_selector('table', timeout=10000)
                except:
                    print("  ⚠️ 데이터 로딩 실패 - 건너뜀")
                    browser.close()
                    return
                
                print("  → 데이터 추출 중...")
                rows = page.query_selector_all('tbody tr')
                
                count = 0
                for row in rows[:15]:
                    try:
                        tds = row.query_selector_all('td')
                        if len(tds) < 3:
                            continue
                        
                        title_elem = None
                        date_elem = None
                        
                        for td in tds:
                            link = td.query_selector('a')
                            if link and not title_elem:
                                title_elem = link
                        
                        if len(tds) >= 4:
                            date_elem = tds[-2]
                        
                        if title_elem:
                            title = title_elem.inner_text().strip()
                            href = title_elem.get_attribute('href') or ''
                            date = date_elem.inner_text().strip() if date_elem else ''
                            
                            if href.startswith('http'):
                                link = href
                            else:
                                link = "https://portal.kosha.or.kr" + href
                            
                            self.results['kosha_notice'].append({
                                'title': title,
                                'date': date,
                                'link': link,
                                'source': '산업안전포털'
                            })
                            count += 1
                    except:
                        continue
                
                browser.close()
            
            print(f"  ✅ {len(self.results['kosha_notice'])}건 수집 완료")
            
        except Exception as e:
            print(f"  ⚠️ 접속 불가 - 건너뜀")
    
    def scrape_kosha_with_requests(self):
        """산업안전포털 공지사항 수집 (requests 사용)"""
        try:
            url = "https://portal.kosha.or.kr/community/notice"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, timeout=15, headers=headers)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 테이블에서 데이터 추출 시도
            table = soup.find('table')
            if table:
                rows = table.find_all('tr')[1:]  # 헤더 제외
                
                for row in rows[:15]:
                    try:
                        link_tag = row.find('a')
                        if not link_tag:
                            continue
                        
                        title = link_tag.get_text(strip=True)
                        href = link_tag.get('href', '')
                        
                        if href.startswith('http'):
                            link = href
                        else:
                            link = "https://portal.kosha.or.kr" + href
                        
                        # 날짜 찾기
                        tds = row.find_all('td')
                        date = ''
                        for td in tds:
                            text = td.get_text(strip=True)
                            if '.' in text and len(text) < 15:
                                date = text
                                break
                        
                        self.results['kosha_notice'].append({
                            'title': title,
                            'date': date,
                            'link': link,
                            'source': '산업안전포털'
                        })
                    except:
                        continue
            
            print(f"  ✅ {len(self.results['kosha_notice'])}건 수집 완료")
        except Exception as e:
            print(f"  ⚠️ 접속 불가 - 건너뜀")
    
    def scrape_major_accidents(self):
        """중대재해 발생알림 수집"""
        print("🚨 중대재해 발생알림 수집 중...")
        
        if not PLAYWRIGHT_AVAILABLE:
            print("  ⚠️ Playwright 미설치 - 건너뜀")
            return
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                page = context.new_page()
                page.set_default_timeout(20000)
                
                print("  → 페이지 로딩 중...")
                try:
                    page.goto(
                        "https://portal.kosha.or.kr/archive/imprtnDsstrAlrame/CSADV50000/CSADV50000M02",
                        wait_until='domcontentloaded', timeout=15000
                    )
                except:
                    print("  ⚠️ 페이지 로딩 시간 초과 - 건너뜀")
                    browser.close()
                    return
                
                # 약간만 대기
                page.wait_for_timeout(2000)
                
                # 여러 선택자 시도
                print("  → 데이터 추출 중...")
                selectors = [
                    '.card-list .card-item',
                    'article',
                    '.list-item',
                    '[class*="card"]'
                ]
                
                cards = []
                for selector in selectors:
                    try:
                        cards = page.query_selector_all(selector)
                        if len(cards) > 0:
                            break
                    except:
                        continue
                
                if cards:
                    for card in cards[:5]:
                        try:
                            title = ''
                            title_selectors = ['.card-title', 'h3', 'h4', '.title', 'a']
                            
                            for ts in title_selectors:
                                title_elem = card.query_selector(ts)
                                if title_elem:
                                    title = title_elem.inner_text().strip()
                                    break
                            
                            if not title:
                                title = card.inner_text().strip()[:100]
                            
                            date = ''
                            date_selectors = ['.card-date', '.date', 'time', 'span']
                            for ds in date_selectors:
                                date_elem = card.query_selector(ds)
                                if date_elem:
                                    date_text = date_elem.inner_text().strip()
                                    if len(date_text) > 0 and len(date_text) < 20:
                                        date = date_text
                                        break
                            
                            if title:
                                self.results['major_accident'].append({
                                    'title': title,
                                    'date': date or self.today,
                                    'source': '안전보건공단'
                                })
                        except:
                            continue
                
                browser.close()
            
            print(f"  ✅ {len(self.results['major_accident'])}건 수집 완료")
            
        except Exception as e:
            print(f"  ⚠️ 접속 불가 - 건너뜀")
    
    def scrape_labor_news(self):
        """매일노동뉴스 안전과 건강 코너 수집"""
        print("📰 매일노동뉴스 수집 중...")
        
        try:
            url = "https://www.labortoday.co.kr/news/articleList.html?sc_section_code=S1N7&view_type=sm"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, timeout=30, headers=headers)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 여러 선택자 시도
            selectors = [
                '.article-list .article-item',
                'article',
                '.list-group .list-group-item',
                'table tbody tr'
            ]
            
            articles = []
            for selector in selectors:
                articles = soup.select(selector)
                if len(articles) > 0:
                    break
            
            # 테이블 형식인 경우
            if not articles:
                table = soup.find('table')
                if table:
                    rows = table.find_all('tr')[1:]  # 헤더 제외
                    for row in rows[:15]:
                        try:
                            link_tag = row.find('a')
                            if not link_tag:
                                continue
                            
                            title = link_tag.get_text(strip=True)
                            href = link_tag.get('href', '')
                            
                            # 링크 처리
                            if href.startswith('http'):
                                link = href
                            elif href.startswith('/'):
                                link = "https://www.labortoday.co.kr" + href
                            else:
                                link = "https://www.labortoday.co.kr/news/" + href
                            
                            # 날짜 찾기
                            date_text = ''
                            tds = row.find_all('td')
                            for td in tds:
                                text = td.get_text(strip=True)
                                if '.' in text and len(text) < 20:  # 날짜 형식 추정
                                    date_text = text
                                    break
                            
                            self.results['labor_news'].append({
                                'title': title,
                                'date': date_text,
                                'link': link,
                                'source': '매일노동뉴스'
                            })
                        except:
                            continue
            else:
                # 기사 리스트 형식
                for article in articles[:15]:
                    try:
                        # 제목과 링크 찾기
                        title_tag = article.find('a') or article.select_one('.article-title a')
                        if not title_tag:
                            continue
                        
                        title = title_tag.get_text(strip=True)
                        href = title_tag.get('href', '')
                        
                        # 링크 처리
                        if href.startswith('http'):
                            link = href
                        elif href.startswith('/'):
                            link = "https://www.labortoday.co.kr" + href
                        else:
                            link = "https://www.labortoday.co.kr/news/" + href
                        
                        # 날짜 찾기
                        date_tag = article.select_one('.article-date') or article.find('time')
                        date = date_tag.get_text(strip=True) if date_tag else ''
                        
                        self.results['labor_news'].append({
                            'title': title,
                            'date': date,
                            'link': link,
                            'source': '매일노동뉴스'
                        })
                    except:
                        continue
            
            print(f"  ✅ {len(self.results['labor_news'])}건 수집 완료")
            
        except Exception as e:
            print(f"  ❌ 수집 실패: {e}")
    
    def search_bigkinds_news(self, keywords: str = "산업안전 중대재해"):
        """Bigkinds에서 뉴스 검색"""
        print(f"🔍 Bigkinds 뉴스 검색 중 (키워드: {keywords})...")
        
        if not PLAYWRIGHT_AVAILABLE:
            print("  ⚠️ Playwright 미설치 - 건너뜀")
            return
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                page = context.new_page()
                page.set_default_timeout(20000)
                
                print("  → 검색 페이지 접속 중...")
                try:
                    # 통합검색 페이지로 이동
                    page.goto("https://www.bigkinds.or.kr/v2/news/search.do", 
                             wait_until='domcontentloaded', timeout=15000)
                    page.wait_for_timeout(2000)
                except:
                    print("  ⚠️ 페이지 접속 실패 - 건너뜀")
                    browser.close()
                    return
                
                # 검색어 입력
                try:
                    search_box = page.query_selector('input[type="text"]') or page.query_selector('#search-input')
                    if search_box:
                        search_box.fill(keywords)
                        page.wait_for_timeout(500)
                        
                        # 검색 버튼 클릭
                        search_btn = page.query_selector('button[type="submit"]') or page.query_selector('.btn-search')
                        if search_btn:
                            search_btn.click()
                            page.wait_for_timeout(3000)
                        else:
                            # 엔터키로 검색
                            search_box.press('Enter')
                            page.wait_for_timeout(3000)
                except:
                    print("  ⚠️ 검색 실행 실패 - 건너뜀")
                    browser.close()
                    return
                
                print("  → 검색 결과 추출 중...")
                
                # 검색 결과 추출
                # Bigkinds는 동적 로딩이므로 여러 선택자 시도
                selectors = [
                    '.news-item',
                    '.search-result-item',
                    'article',
                    '.list-item',
                    '[class*="result"]'
                ]
                
                results = []
                for selector in selectors:
                    try:
                        results = page.query_selector_all(selector)
                        if len(results) > 0:
                            break
                    except:
                        continue
                
                count = 0
                for result in results[:10]:  # 최근 10건만
                    try:
                        # 제목 찾기
                        title = ''
                        title_selectors = ['h3', 'h4', '.title', 'a', 'strong']
                        for ts in title_selectors:
                            title_elem = result.query_selector(ts)
                            if title_elem:
                                title = title_elem.inner_text().strip()
                                if len(title) > 10:  # 의미있는 제목
                                    break
                        
                        # 링크 찾기
                        link = ''
                        link_elem = result.query_selector('a')
                        if link_elem:
                            href = link_elem.get_attribute('href') or ''
                            if href.startswith('http'):
                                link = href
                            elif href.startswith('/'):
                                link = "https://www.bigkinds.or.kr" + href
                        
                        # 날짜 찾기
                        date = ''
                        date_selectors = ['.date', 'time', 'span', '.info']
                        for ds in date_selectors:
                            date_elem = result.query_selector(ds)
                            if date_elem:
                                date_text = date_elem.inner_text().strip()
                                # 날짜 형식 확인 (YYYY-MM-DD, YYYY.MM.DD 등)
                                if any(char in date_text for char in ['-', '.', '/']) and len(date_text) < 15:
                                    date = date_text
                                    break
                        
                        # 언론사 찾기
                        source = 'Bigkinds'
                        source_selectors = ['.source', '.press', '.media']
                        for ss in source_selectors:
                            source_elem = result.query_selector(ss)
                            if source_elem:
                                source_text = source_elem.inner_text().strip()
                                if source_text:
                                    source = source_text
                                    break
                        
                        # 안전보건 관련 키워드 필터링
                        safety_keywords = ['안전', '산재', '중대재해', '재해', '사고', '보건', '위험']
                        if title and any(kw in title for kw in safety_keywords):
                            self.results['bigkinds_news'].append({
                                'title': title,
                                'date': date or self.today,
                                'link': link,
                                'source': source
                            })
                            count += 1
                    except:
                        continue
                
                browser.close()
            
            print(f"  ✅ {len(self.results['bigkinds_news'])}건 수집 완료")
            
        except Exception as e:
            print(f"  ⚠️ 검색 실패 - 건너뜀")
    
    def search_additional_news(self):
        """추가 언론기사 검색"""
        print("🔍 추가 언론기사 검색 중...")
        print("  ℹ️  Bigkinds 검색을 사용하려면 search_bigkinds_news() 메서드를 직접 호출하세요")
        print("  ⏭️  추가 뉴스 검색은 별도 구현 필요")
    
    def run_all_scrapers(self):
        """모든 스크래퍼 실행"""
        print(f"\n{'='*60}")
        print(f"🤖 일일 동향 데이터 수집 시작: {self.today}")
        print(f"{'='*60}\n")
        
        self.scrape_moel_press_release()
        time.sleep(2)  # 서버 부하 방지
        
        self.scrape_kosha_with_playwright()
        time.sleep(2)
        
        self.scrape_major_accidents()
        time.sleep(2)
        
        self.scrape_labor_news()
        time.sleep(2)
        
        self.search_additional_news()
        
        print(f"\n{'='*60}")
        print(f"✅ 데이터 수집 완료!")
        print(f"{'='*60}\n")
        
        return self.results
    
    def get_summary(self):
        """수집된 데이터 요약"""
        total = sum(len(v) for v in self.results.values())
        summary = {
            'total': total,
            'by_source': {k: len(v) for k, v in self.results.items()}
        }
        return summary


if __name__ == "__main__":
    scraper = SafetyNewsScraper()
    results = scraper.run_all_scrapers()
    summary = scraper.get_summary()
    
    print("📊 수집 결과 요약:")
    print(f"  총 {summary['total']}건")
    for source, count in summary['by_source'].items():
        print(f"  - {source}: {count}건")
