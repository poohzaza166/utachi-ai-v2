from voicevox import Client
import asyncio


async def main(message: str, filename: str):
    print(message)
    async with Client() as client:
        audio_query = await client.create_audio_query(
            message, speaker=4
        )
        audio_query.speed_scale = 1.18
        # return await audio_query.synthesis(speaker=4)
        with open(filename, "wb") as f:
            f.write(await audio_query.synthesis(speaker=4))

if __name__ == "__main__":
    asyncio.run(main("ello"))