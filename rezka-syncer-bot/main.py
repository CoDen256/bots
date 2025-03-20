import asyncio
import subprocess

from hdrezka import Search

async def main():
    search = Search('Breaking Bad')
    page = await search.get_page(1)
    player = await page[0].player
    print(player.post.name, end='\n\n')

    stream = await player.get_stream(1, 1, 238)  # raise AJAXFail if invalid episode or translator
    eps = await player.get_episodes(238)  # raise AJAXFail if invalid episode or translator
    video = stream.video
    videos = await video.raw_data
    print(videos['1080p'])  # best quality (.m3u8)

    subtitles = stream.subtitles
    print(subtitles)  # subtitles.ru.url or subtitles['Русский'].url


# if __name__ == '__main__': asyncio.run(main())

output = subprocess.Popen(['./dl', "-b", "https://hdrezka.website/series/comedy/1814-ofis-2005.html#t:238-s:2-e:22"], stdout=subprocess.PIPE).communicate()[0]
print(output)