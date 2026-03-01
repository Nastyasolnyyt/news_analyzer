from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.errors.post_analysis import PostAnalysisNotFoundException
from src.application.schemas.post_analysis import PostAnalysisDTO
from src.infrastructure.postgres.models.post_analysis import PostAnalysis


class PostAnalysisDBGateWay:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_post_analysis(self, post_id: int) -> PostAnalysisDTO:
        result = await self.session.execute(
            select(PostAnalysis).where(
                PostAnalysis.post_id == post_id,
            )
        )
        post_analysis = result.scalars().first()
        if post_analysis is None:
            raise PostAnalysisNotFoundException()
        return PostAnalysisDTO.model_validate(post_analysis.as_dict())
