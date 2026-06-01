from fastapi import APIRouter

from app.core.branding import BrandingConfig, load_branding

router = APIRouter(tags=["branding"])


@router.get("/branding", response_model=BrandingConfig)
async def get_branding():
    return load_branding()
