from typing import Annotated, Any, Literal, Optional, TypeVar, Union
from pydantic import BaseModel, Field, model_serializer
from abc import ABC

OnlyReceive = TypeVar("OnlyReceive", bound=Any)
OnlySend = TypeVar("OnlySend", bound=Any)


class MessageComponent(BaseModel, ABC):
    """消息组件

    注意：带有 Annotated[..., OnlySend] 的是仅发送组件，带有 Annotated[..., OnlyReceive] 的是仅接收组件，不要搞混！

    Attributes:
        comp_type: 消息组件类型
        ...: 参见相关的 OneBot 11 标准文档
    """

    comp_type: str = Field(description="组件类型", alias="type")

    @model_serializer
    def model_ser(self) -> dict[str, Any]:
        return {
            "type": self.comp_type,
            "data": self.model_dump(mode="json", exclude={"type"}),
        }

    def to_cqcode(self) -> str:
        """转换成 CQ 码。不保证完全正确，如果有特殊组件，请自行实现该方法。如有问题，请提 Issue。

        Returns:
            CQ 码
        """
        params: list[str] = []
        for k, _ in self.model_fields.items():
            if k == "comp_type":
                continue
            params.append(f"{k}={self.__getattribute__(k)}")

        return f'[CQ:{self.comp_type},{",".join(params)}]'  # 用列表推导式太乱了，这里用传统形式写

    def __eq__(self, another: Union["MessageComponent", str, object]) -> bool:
        """比较

        Args:
            another: 另一个对象

        Returns:
            当 another 是一个 MessageComponent 时，比较它们的 CQ 码；
            当 another 是一个 str 时，比较该组件的 CQ 码是否和其相同（由于 Text 重载了 to_cqcode 方法，因此 Text 组件只会比较文本内容是否相同）；
            当 another 不是上述任何一种时，比较它们的 **内存地址**。（也就是 is 运算符）
        """
        if isinstance(another, MessageComponent):
            return self.to_cqcode() == another.to_cqcode()
        elif isinstance(another, str):
            return self.to_cqcode() == another
        else:
            return self is another

    def __repr__(self) -> str:
        return self.to_cqcode()


# Attention!
# All the code below the comment are generated by AI according OneBot 11 Standrad.
# The developer does not approve these code are all right.
# Please check it before you use it.


class Text(MessageComponent):
    comp_type: str = "text"
    text: str = Field(description="纯文本")

    def __init__(self, text: str) -> None:
        BaseModel.__init__(self, text=text)

    def to_cqcode(self) -> str:
        return self.text


class Face(MessageComponent):
    comp_type: str = "face"
    id: str = Field(description="QQ 表情 ID")

    def __init__(self, id: int | str) -> None:
        BaseModel.__init__(self, id=str(id))


class Image(MessageComponent):
    comp_type: str = "image"
    file: str = Field(description="图片文件路径或 URL")
    type: Optional[Literal["flash"]] = Field(
        description="图片类型，flash 表示闪照，无此参数表示普通图片"
    )
    url: Optional[Annotated[str, OnlyReceive]] = Field(description="图片 URL")
    cache: Annotated[Optional[bool], OnlySend] = Field(
        default=True,
        description="只在通过网络 URL 发送时有效，表示是否使用已缓存的文件",
    )
    proxy: Annotated[Optional[bool], OnlySend] = Field(
        default=True,
        description="只在通过网络 URL 发送时有效，表示是否通过代理下载文件（需通过环境变量或配置文件配置代理）",
    )
    timeout: Annotated[Optional[int], OnlySend] = Field(
        default=30,
        description="只在通过网络 URL 发送时有效，单位秒，表示下载网络文件的超时时间，默认不超时",
    )


class Record(MessageComponent):
    comp_type: str = "record"
    file: str = Field(description="语音文件路径")
    url: Annotated[Optional[str], OnlyReceive] = Field(description="语音 URL")
    cache: Annotated[Optional[bool], OnlySend] = Field(
        default=True,
        description="只在通过网络 URL 发送时有效，表示是否使用已缓存的文件",
    )
    proxy: Annotated[Optional[bool], OnlySend] = Field(
        default=True,
        description="只在通过网络 URL 发送时有效，表示是否通过代理下载文件（需通过环境变量或配置文件配置代理）",
    )
    timeout: Annotated[Optional[int], OnlySend] = Field(
        default=30,
        description="只在通过网络 URL 发送时有效，单位秒，表示下载网络文件的超时时间，默认不超时",
    )


class Video(MessageComponent):
    comp_type: str = "video"
    file: Optional[str] = Field(description="视频文件路径")
    url: Annotated[Optional[str], OnlyReceive] = Field(description="视频 URL")
    cache: Annotated[Optional[bool], OnlySend] = Field(
        default=True,
        description="只在通过网络 URL 发送时有效，表示是否使用已缓存的文件",
    )
    proxy: Annotated[Optional[bool], OnlySend] = Field(
        default=True,
        description="只在通过网络 URL 发送时有效，表示是否通过代理下载文件（需通过环境变量或配置文件配置代理）",
    )
    timeout: Annotated[Optional[int], OnlySend] = Field(
        default=30,
        description="只在通过网络 URL 发送时有效，单位秒，表示下载网络文件的超时时间，默认不超时",
    )


class At(MessageComponent):
    comp_type: str = "at"
    qq: str = Field(description="@的 QQ 号，all 表示全体成员")

    def __init__(self, qq: str) -> None:
        BaseModel.__init__(self, qq=qq)


class Rps(MessageComponent):
    comp_type: str = "rps"


class Dice(MessageComponent):
    comp_type: str = "dice"


class Shake(MessageComponent):
    comp_type: str = "shake"


class Poke(MessageComponent):
    comp_type: str = "poke"
    type: int = Field(description="类型，见 Mirai 的 PokeMessage 类")
    id: int = Field(description="ID")
    name: Annotated[Optional[str], OnlyReceive] = Field(description="表情名")


class Anonymous(MessageComponent):
    comp_type: str = "anonymous"
    ignore: Annotated[Optional[bool], OnlySend] = Field(
        default=None, description="可选，表示无法匿名时是否继续发送"
    )


class Share(MessageComponent):
    comp_type: str = "share"
    url: str = Field(description="URL")
    title: str = Field(description="标题")
    content: Optional[str] = Field(description="发送时可选，内容描述")
    image: Optional[str] = Field(description="发送时可选，图片 URL")


class Contact(MessageComponent):
    comp_type: str = "contact"
    type: Literal["qq", "group"] = Field(description="推荐类型")
    id: str = Field(description="被推荐人的 QQ 号或群号")


class Location(MessageComponent):
    comp_type: str = "location"
    lat: str = Field(description="纬度")
    lon: str = Field(description="经度")
    title: Optional[str] = Field(description="发送时可选，标题")
    content: Optional[str] = Field(description="发送时可选，内容描述")


class Music(MessageComponent):
    comp_type: str = "music"
    type: Annotated[str, OnlySend] = Field(description="音乐类型")
    id: Annotated[str, OnlySend] = Field(description="歌曲 ID")


class Reply(MessageComponent):
    comp_type: str = "reply"
    id: str = Field(description="回复时引用的消息 ID")

    def __init__(self, id: str) -> None:
        BaseModel.__init__(self, id=id)


class Forward(MessageComponent):
    comp_type: str = "forward"
    id: Annotated[str, OnlyReceive] = Field(description="合并转发 ID")

    def __init__(self, id: str) -> None:
        BaseModel.__init__(self, id=id)


class Node(MessageComponent):
    comp_type: str = "node"
    id: str = Field(description="转发的消息 ID")
    user_id: str = Field(description="发送者 QQ 号")
    nickname: str = Field(description="发送者昵称")
    content: str | list[MessageComponent] = Field(description="消息内容")


class Xml(MessageComponent):
    comp_type: str = "xml"
    data: str = Field(description="XML 内容")

    def __init__(self, data: str) -> None:
        BaseModel.__init__(self, data=data)


class Json(MessageComponent):
    comp_type: str = "json"
    data: str = Field(description="JSON 内容")

    def __init__(self, data: str) -> None:
        BaseModel.__init__(self, data=data)


# Attention!
# All the code above the comment are generated by AI according OneBot 11 Standrad.
# The developer does not approve these code are all right.
# Please check them before you use them.


__all__ = [
    "Text",
    "Face",
    "Image",
    "Record",
    "Video",
    "At",
    "Rps",
    "Dice",
    "Shake",
    "Poke",
    "Anonymous",
    "Share",
    "Contact",
    "Location",
    "Music",
    "Reply",
    "Forward",
    "Node",
    "Xml",
]
