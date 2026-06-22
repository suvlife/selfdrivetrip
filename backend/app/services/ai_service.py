"""AI-powered route generation service using OpenAI-compatible API."""

import json
import logging
from typing import List, Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """你是一位专业的中国自驾游路线规划专家。你擅长根据用户的出发城市、目的地、出行时间、天数和预算，设计详细、可行、有趣的自驾游路线。

请根据用户提供的信息，生成3到5条不同风格的自驾游路线方案。每条路线必须包含完整的行程安排，并以**严格的JSON格式**返回。

## 输出格式要求
必须返回一个JSON对象，格式如下：
```json
{
  "routes": [
    {
      "title": "路线名称",
      "theme": "路线主题风格",
      "departure": "出发城市",
      "destination": "目的地城市",
      "total_distance": 总里程(公里, 数字),
      "total_duration": 总驾驶时长(小时, 数字),
      "budget": 预估总预算(元, 数字),
      "day_plans": [
        {
          "day_number": 1,
          "date": "第1天",
          "theme": "当天主题",
          "day_distance": 当天里程(公里),
          "day_duration": 当天驾驶时长(小时),
          "day_cost": 当天预估花费(元),
          "segments": [
            {
              "from_name": "起点名称",
              "to_name": "终点名称",
              "distance": 距离(公里),
              "duration": 驾驶时长(小时),
              "toll_cost": 过路费(元),
              "fuel_cost": 油费(元),
              "polyline": [[经度, 纬度], [经度, 纬度]],
              "sort_order": 0
            }
          ],
          "pois": [
            {
              "type": "scenic/restaurant/hotel/gas_station/charging/waypoint",
              "name": "景点/地点名称",
              "lat": 纬度,
              "lng": 经度,
              "rating": 评分(0-5),
              "price_level": "价格等级",
              "description": "简短介绍",
              "duration_minutes": 建议游玩分钟数,
              "sort_order": 0
            }
          ],
          "meals": [
            {
              "type": "breakfast/lunch/dinner",
              "restaurant_name": "餐厅名称",
              "cuisine_type": "菜系类型",
              "cost_per_person": 人均消费(元),
              "rating": 评分(0-5),
              "recommendation": "推荐理由"
            }
          ],
          "hotels": [
            {
              "name": "酒店名称",
              "lat": 纬度,
              "lng": 经度,
              "price_per_night": 每晚价格(元),
              "rating": 评分(0-5),
              "address": "地址",
              "phone": "电话"
            }
          ]
        }
      ]
    }
  ]
}
```

## 设计原则
1. **合理性**：每天的驾驶里程建议在200-400公里之间，避免疲劳驾驶
2. **丰富性**：每天包含2-3个景点、推荐的餐厅和住宿
3. **准确性**：距离和时间的估算要符合实际自驾经验
4. **预算合理**：根据用户预算控制总花费
5. **季节性**：考虑出行月份的天气和景色特点
6. **多样性**：不同路线应有不同的风格（如：经典路线、小众路线、亲子路线、美食路线、文化路线等）

请确保返回的JSON是有效的、可以解析的。不要包含任何额外的说明文字，只返回JSON。"""


async def call_llm(prompt: str, model: Optional[str] = None) -> str:
    """Call the OpenAI-compatible API and return the response text."""
    api_key = settings.AI_API_KEY
    base_url = settings.AI_API_BASE_URL.rstrip("/")
    model_name = model or settings.AI_MODEL

    if not api_key:
        logger.warning("AI_API_KEY not configured, using fallback mock data")
        return ""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.8,
        "max_tokens": 8192,
        "response_format": {"type": "json_object"},
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            resp = await client.post(f"{base_url}/chat/completions", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            return content.strip()
        except Exception as e:
            logger.error(f"LLM API call failed: {e}")
            raise


def parse_llm_response(content: str) -> dict:
    """Parse JSON from LLM response, handling markdown fences if present."""
    if not content:
        return {"routes": []}

    # Remove markdown code fences if present
    text = content.strip()
    if text.startswith("```"):
        # Find the first ``` and last ```
        first = text.find("\n")
        last = text.rfind("```")
        if first != -1 and last != -1:
            text = text[first:last].strip()
        elif first != -1:
            text = text[first:].strip()
        else:
            text = text.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        logger.error(f"Failed to parse LLM response as JSON: {text[:500]}")
        return {"routes": []}


def build_user_prompt(
    departure_city: str,
    destination_city: str,
    month: str,
    days: int,
    trip_type: str,
    adults: int,
    children: int,
    car_type: str,
    budget: float,
    theme: str = "",
) -> str:
    """Build the user prompt for the LLM."""
    prompt_parts = [
        f"请为以下自驾游需求设计{3 if not theme else '3-5'}条不同风格的路线方案：\n",
        f"出发城市：{departure_city}",
        f"目的地：{destination_city}",
        f"出行月份：{month}",
        f"行程天数：{days}天",
        f"旅行类型：{trip_type}",
        f"成人：{adults}人",
        f"儿童：{children}人",
        f"车型：{car_type}",
        f"预算：{budget}元",
    ]

    if theme:
        prompt_parts.append(f"主题风格：{theme}")
        prompt_parts.append(f"\n请重点围绕「{theme}」这一主题来设计路线。")

    prompt_parts.append(f"\n请生成{3 if not theme else '3-5'}条完整路线，每条路线包含{days}天的详细行程安排。")
    prompt_parts.append("\n注意：每条路线的总预算应控制在{budget}元左右。")

    # Adjust per-day distance based on trip type
    if "长途" in trip_type:
        prompt_parts.append("\n每天驾驶里程可以在300-500公里之间。")
    elif "休闲" in trip_type or "短途" in trip_type:
        prompt_parts.append("\n每天驾驶里程建议在100-250公里之间。")
    else:
        prompt_parts.append("\n每天驾驶里程建议在200-400公里之间。")

    return "\n".join(prompt_parts)


async def generate_routes(
    departure_city: str,
    destination_city: str,
    month: str,
    days: int,
    trip_type: str,
    adults: int,
    children: int,
    car_type: str,
    budget: float,
    theme: str = "",
) -> List[dict]:
    """Generate route plans using the LLM. Returns list of route dicts."""
    prompt = build_user_prompt(
        departure_city, destination_city, month, days,
        trip_type, adults, children, car_type, budget, theme,
    )

    try:
        content = await call_llm(prompt)
        result = parse_llm_response(content)
        routes = result.get("routes", [])

        # Ensure each route has proper metadata
        for route in routes:
            route.setdefault("departure", departure_city)
            route.setdefault("destination", destination_city)
            route.setdefault("car_type", car_type)
            route.setdefault("adults", adults)
            route.setdefault("children", children)
            route.setdefault("trip_type", trip_type)
            route.setdefault("status", "draft")

            # Ensure day_plans exist
            day_plans = route.get("day_plans", [])
            if not day_plans:
                # Create a basic day plan structure
                day_plans = [
                    {
                        "day_number": i + 1,
                        "date": f"第{i+1}天",
                        "theme": "",
                        "day_distance": 0,
                        "day_duration": 0,
                        "day_cost": 0,
                        "segments": [],
                        "pois": [],
                        "meals": [],
                        "hotels": [],
                    }
                    for i in range(days)
                ]
                route["day_plans"] = day_plans

        return routes

    except Exception as e:
        logger.error(f"Route generation failed: {e}")
        raise
