"""
crawler.tasks
=============

This module contains integration tasks for synchronising this DB with the metadata used in the rest of the discovery layer.

.. autofunction:: sync_from_crawler

.. autofunction:: sync_updates_from_crawler

"""
from celery import shared_task
from django.db import connection
from .models import WebDocument
from metadata.tasks import insert_resource_from_row
from metadata.tasks import update_resource_from_row
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

@shared_task
def sync_from_crawler(limit=None):
    """dispatch metadata.Resource inserts for **new** crawler.WebDocuments"""
    DEFAULT_LIMIT = 12000 # 2/3 of throughput given 3 minute beat
    if limit is None:
        limit = DEFAULT_LIMIT
    if type(limit) != type(9):
        try:
            limit = int(limit)
        except:
            limit = DEFAULT_LIMIT
    logger.debug('sync_from_crawler: limit={0}'.format(limit,))

    raw_sql = '''
        select
            url, hash, protocol, "contentType",
            host, port, path, "lastFetchDateTime"
        from "webDocuments"
        where "fetchStatus" = 'downloaded'
        and url not in (
            select url
            from metadata_resource
        )
        LIMIT %d''' % limit
    logger.debug(raw_sql)

    cursor = connection.cursor()
    cursor.execute(raw_sql)
    for row in cursor:
        row = list(row)
        row[7] = row[7].isoformat()
        logger.debug('sync_from_crawler: dispatching {0}'.format(row,))
        insert_resource_from_row.delay(row)

@shared_task
def delete_metadata_when_missing(limit=None):
    """delete from metadata.Resource when the crawler finds it missing

    per #76... delete if

    if metadata.url == webDocument.url AND:

    (metadata.hash is not null AND webDocument.hash is null) OR
    (webDocument.httpCode != (2xx or 3xx)) OR
    (fetchStatus == )


    "failed", "notfound", "redirected" sh
    """
    DEFAULT_LIMIT = 1000
    if limit is None:
        limit = DEFAULT_LIMIT
    if type(limit) != type(9):
        try:
            limit = int(limit)
        except:
            limit = DEFAULT_LIMIT

    raw_sql = '''
        select
            wd.url
        from
            "webDocuments" as wd
        where wd."fetchStatus" in ("failed", "notfound", "redirected")
        and wd.url in (select url from metadata_resource)
        LIMIT %d''' % limit
    cursor = connection.cursor()
    cursor.execute(raw_sql)
    for row in cursor:
        delete_resource_with_url.delay(row[0])


@shared_task
def sync_updates_from_crawler(limit=None):
    """dispatch metadata.Resource updates for **changed** crawler.WebDocuments"""
    DEFAULT_LIMIT = 1000
    if limit is None:
        limit = DEFAULT_LIMIT
    if type(limit) != type(9):
        try:
            limit = int(limit)
        except:
            limit = DEFAULT_LIMIT

    raw_sql = '''
        select
            wd.url, wd.hash, wd.protocol, wd."contentType",
            wd.host, wd.port, wd.path, wd."lastFetchDateTime"
        from
            "webDocuments" as wd,
            metadata_resource as mr
        where wd."fetchStatus" = 'downloaded'
        and wd.url = mr.url
        and wd.hash != mr.hash
        LIMIT %d''' % limit
    cursor = connection.cursor()
    cursor.execute(raw_sql)
    for row in cursor:
        row=list(row)
        row[7] = row[7].isoformat()
        update_resource_from_row.delay(row)

