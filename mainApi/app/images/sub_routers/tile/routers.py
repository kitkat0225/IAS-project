import asyncio
import concurrent

import pydantic
from PIL import Image
from bson import ObjectId

from fastapi import (
    APIRouter,
    Depends,
    status,
    UploadFile,
    File, Form, HTTPException
)
from motor.motor_asyncio import AsyncIOMotorDatabase
from starlette.responses import FileResponse

from mainApi.app.auth.auth import get_current_user

from typing import List

from mainApi.app.db.mongodb import get_database
from mainApi.app.images.sub_routers.tile.models import AlignNaiveRequest, TileModelDB, AlignedTiledModel, BaseTileModel
from mainApi.app.images.utils.align_tiles import align_tiles_naive, align_ashlar
from mainApi.app.images.utils.file import save_upload_file, add_image_tiles
from mainApi.app.images.utils.folder import get_user_cache_path, clear_path
from mainApi.app.auth.models.user import UserModelDB, PyObjectId

router = APIRouter(
    prefix="/tile",
    tags=["tile"],
)


@router.post("/upload_image_tiles",
             response_description="Upload Image Tiles",
             status_code=status.HTTP_201_CREATED,
             response_model=List[TileModelDB])
async def upload_image_tiles(files: List[UploadFile] = File(...),
                             absolute_client_path: str = Form(...),
                             clear_previous: bool = Form(True),
                             current_user: UserModelDB = Depends(get_current_user),
                             db: AsyncIOMotorDatabase = Depends(get_database)) -> List[TileModelDB]:
    """
    Saves the uploaded tiles to the cache-storage folder/volume under the user_id of the current_user

    Front end should include a validator that checks if the file has already been uploaded and then reject it.
    No validation is done in the backend
    """

    return await add_image_tiles(files=files,
                                 absolute_client_path=absolute_client_path,
                                 clear_previous=clear_previous,
                                 current_user=current_user,
                                 db=db)


@router.get("/list",
            response_description="Upload Image Tiles",
            response_model=List[TileModelDB],
            status_code=status.HTTP_200_OK)
async def get_tile_list(current_user: UserModelDB = Depends(get_current_user),
                        db: AsyncIOMotorDatabase = Depends(get_database)) -> List[TileModelDB]:
    tiles = await db['tile-image-cache'].find({'user_id': current_user.id}).to_list(None)
    return pydantic.parse_obj_as(List[TileModelDB], tiles)


@router.get("/file",
            response_description="Download Image Tile",
            status_code=status.HTTP_200_OK)
async def get_file(tile_id: str or PyObjectId or ObjectId,
                   current_user: UserModelDB = Depends(get_current_user),
                   db: AsyncIOMotorDatabase = Depends(get_database)) -> FileResponse:

    tile = await db['tile-image-cache'].find_one({'user_id': current_user.id, '_id': ObjectId(tile_id)})

    if tile is None:
        return status.HTTP_404_NOT_FOUND

    tile = pydantic.parse_obj_as(TileModelDB, tile)

    return FileResponse(path=tile.absolute_backend_path, filename=tile.file_name)


@router.post("/update",
             response_description="Update Image Tiles",
             status_code=status.HTTP_200_OK)
async def update_tiles(tiles: List[TileModelDB],
                       current_user: UserModelDB = Depends(get_current_user),
                       db: AsyncIOMotorDatabase = Depends(get_database)):
    # make sure we are not trying to alter any tiles we do not own
    # we check this first and if they are trying to update any un owned docs we dont update any
    for tile in tiles:
        if tile.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Cannot update tile that does not belong to user",
                headers={"WWW-Authenticate": "Bearer"},
            )

    for tile in tiles:
        result = await db['tile-image-cache'].replace_one({'_id': tile.id}, tile.dict(exclude={'id'}))


@router.post("/delete",
             response_description="Tiles Deleted",
             status_code=status.HTTP_200_OK)
async def delete_tiles(tiles: List[BaseTileModel],
                       current_user: UserModelDB = Depends(get_current_user),
                       db: AsyncIOMotorDatabase = Depends(get_database)):
    # make sure we are not trying to delete any tiles we do not own
    # we check this first and if they are trying to delete any un owned docs we dont update any
    for tile in tiles:
        if tile.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Cannot delete tile that does not belong to user",
                headers={"WWW-Authenticate": "Bearer"},
            )

    results = []

    for tile in tiles:
        result = await db['tile-image-cache'].delete_one({'_id': tile.id})
        results.append(result)

    return results


@router.post("/delete_by_id",
             response_description="Tiles Deleted",
             status_code=status.HTTP_200_OK)
async def delete_tiles_by_id(tile_ids: List[str] or List[ObjectId],
                             current_user: UserModelDB = Depends(get_current_user),
                             db: AsyncIOMotorDatabase = Depends(get_database)):
    '''
    Delete Tile by Tile Id.
    Less efficient than the default /delete due to requiring to fetch the tiles prior to deleting them.
    '''
    # make sure we are not trying to delete any tiles we do not own
    # we check this first and if they are trying to delete any un owned docs we dont update any
    # we need to first get the tile to be able to compare it's user_id with the current_user id

    tiles = []

    for tile_id in tile_ids:
        tile = await db['tile-image-cache'].find_one({'_id': ObjectId(tile_id)})
        tiles.append(tile)

    for tile in tiles:
        if tile.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Cannot delete tile that does not belong to user",
                headers={"WWW-Authenticate": "Bearer"},
            )

    results = []

    for tile in tiles:
        result = await db['tile-image-cache'].delete_one({'_id': tile.id})
        results.append(result)

    return results


@router.get("/align_tiles_naive",
            response_description="Align Tiles",
            response_model=List[AlignedTiledModel],
            status_code=status.HTTP_200_OK)
async def _align_tiles_naive(request: AlignNaiveRequest,
                             tiles: List[TileModelDB] = Depends(get_tile_list)) -> List[AlignedTiledModel]:
    """
        performs a naive aligning of the tiles simply based on the given rows and method.
        does not perform any advanced stitching or pixel checking

        Called using concurrent.futures to make it async
    """

    loop = asyncio.get_event_loop()
    with concurrent.futures.ProcessPoolExecutor() as pool:
        aligned_tiles = await loop.run_in_executor(pool, align_tiles_naive, request, tiles)  # await result

        return aligned_tiles


@router.get("/align_tiles_ashlar",
            response_description="Align Tiles",
            # response_model=List[AlignedTiledModel],
            status_code=status.HTTP_200_OK)
async def _align_tiles_ashlar(tiles: List[TileModelDB] = Depends(get_tile_list)) -> any:
    """
        Performs aligning of the tiles using the Ashlar library.

        Called using concurrent.futures to make it async
    """

    loop = asyncio.get_event_loop()
    with concurrent.futures.ProcessPoolExecutor() as pool:
        aligned_tiles = await loop.run_in_executor(pool, align_ashlar, tiles,
                                                   "img_r{row:03}_c{col:03}.tif")  # await result

        return aligned_tiles


@router.get("/export_stitched_image",
            response_description="Export stitched Image",
            response_model=List[AlignedTiledModel],
            status_code=status.HTTP_200_OK)
# async def export_stitched_image(tiles: List[AlignedTiledModel]) -> List[TileModel]:
async def export_stitched_image() -> List[TileModelDB]:
    """ This is meant to called after the images are aligned, so it takes a list of AlignedTiledModel in the body """
    pass
    # loop = asyncio.get_event_loop()
    # with concurrent.futures.ProcessPoolExecutor() as pool:
    #     result = await loop.run_in_executor(pool, cpu_bound)  # wait result
    #     print(result)
