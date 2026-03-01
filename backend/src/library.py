from typing import Any, cast

import boto3
from pydantic import BaseModel, EmailStr, Field


class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr


class Item(ItemCreate):
    id: int


class StorageDB:
    """
    DynamoDB table requirements:
      - Partition key: "id" (Number)
      - Regular items: id>=1 with attributes: name (String), email (String)
      - Metadata item: id=0 reserved, stores next_id (Number)
    """

    _META_ID = 0
    _table: Any

    def __init__(self, table_name: str) -> None:
        boto3_any = cast(Any, boto3)
        self._table = boto3_any.resource("dynamodb").Table(table_name)

    def _alloc_id(self) -> int:
        """
        Atomically allocate a new id by incrementing metadata.next_id.

        We store next_id as "next available id".
        Update sets: next_id = if_not_exists(next_id, 1) + 1
        allocated_id = updated_next_id - 1
        """
        resp: dict[str, Any] = self._table.update_item(
            Key={"id": self._META_ID},
            UpdateExpression="SET next_id = if_not_exists(next_id, :start) + :inc",
            ExpressionAttributeValues={":start": 1, ":inc": 1},
            ReturnValues="UPDATED_NEW",
        )
        updated_next_id = int(resp.get("Attributes", {}).get("next_id", 2))
        return updated_next_id - 1

    def new_item(self, item: ItemCreate) -> Item:
        item_id = self._alloc_id()
        new_item = Item(id=item_id, **item.model_dump())

        self._table.put_item(
            Item={"id": int(new_item.id), "name": new_item.name, "email": new_item.email},
            ConditionExpression="attribute_not_exists(id)",
        )
        return new_item

    def get_item(self, item_id: int) -> Item | None:
        if item_id == self._META_ID:
            return None

        resp: dict[str, Any] = self._table.get_item(Key={"id": int(item_id)}, ConsistentRead=True)
        raw = resp.get("Item")
        if not raw:
            return None

        return Item(
            id=int(raw["id"]), name=str(raw.get("name", "")), email=str(raw.get("email", ""))
        )

    def set_item(self, item_id: int, item: ItemCreate) -> Item | None:
        if item_id == self._META_ID:
            return None

        try:
            self._table.update_item(
                Key={"id": int(item_id)},
                ConditionExpression="attribute_exists(id)",
                UpdateExpression="SET #n = :name, email = :email",
                ExpressionAttributeNames={"#n": "name"},
                ExpressionAttributeValues={":name": item.name, ":email": item.email},
            )
        except Exception as e:  # pragma: no cover (boto3 ClientError is untyped here)
            if e.__class__.__name__ == "ConditionalCheckFailedException":
                code = getattr(e, "response", {}).get("Error", {}).get("Code", "")
                if code == "ConditionalCheckFailedException":
                    return None
            return None

        return Item(id=item_id, **item.model_dump())

    def delete_item(self, item_id: int) -> bool:
        if item_id == self._META_ID:
            return False

        try:
            self._table.delete_item(
                Key={"id": int(item_id)},
                ConditionExpression="attribute_exists(id)",
            )
        except Exception as e:  # pragma: no cover
            if e.__class__.__name__ == "ConditionalCheckFailedException":
                code = getattr(e, "response", {}).get("Error", {}).get("Code", "")
                if code == "ConditionalCheckFailedException":
                    return False
            return False

        return True

    def all_items(self) -> list[Item]:
        items: list[Item] = []
        scan_kwargs: dict[str, Any] = {}

        while True:
            resp: dict[str, Any] = self._table.scan(**scan_kwargs)
            for raw in resp.get("Items", []):
                item_id = int(raw.get("id", -1))
                if item_id == self._META_ID or item_id < 1:
                    continue
                items.append(
                    Item(
                        id=item_id,
                        name=str(raw.get("name", "")),
                        email=str(raw.get("email", "")),
                    )
                )

            last_key = resp.get("LastEvaluatedKey")
            if not last_key:
                break
            scan_kwargs["ExclusiveStartKey"] = last_key

        items.sort(key=lambda it: it.id)
        return items
