import aiohttp

API_KEY = "live_PVulOAfuIGtdjvPDJ3HUjyZ27xF0XCR8W35bhx4wxvLbE90h5zg8Ef2BwJHhUoYa"
API_URL = f"https://api.thecatapi.com/v1/images/search?limit=1&api_key={API_KEY}&"


async def get_cat_info():
    async with aiohttp.ClientSession() as session:
        async with session.get(API_URL) as response:
            cats_list = await response.json()
            for cat in cats_list:
                url = cat.get("url")
    return url
