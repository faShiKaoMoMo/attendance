from enum import Enum


class StatisticsEnum(Enum):
    FAILED = -1  # 失败
    RUNNING = 0  # 执行中
    SUCCESS = 1  # 成功
    NEED_CAPTCHA = 2  # 需要验证码

    @property
    def code(self) -> int:
        return self.value


class ApprovalEnum(Enum):
    PENDING = 0
    APPROVED = 1
    REJECTED = 2

    @property
    def code(self) -> int:
        return self.value
