import datetime
import decimal
import uuid

from sqlalchemy import (
    BINARY,
    DateTime,
    Identity,
    Integer,
    Numeric,
    Unicode,
    func,
    text,
)
from sqlalchemy.orm import Mapped, declared_attr, mapped_column


class AuditMixin:
    """
    Mixin class to add audit fields to a SQLAlchemy model.
    This mixin adds fields for creation and update timestamps, user IDs,
    and a UUID for tracking changes.
    """

    @declared_attr
    def createUser(cls) -> Mapped[str]:
        return mapped_column(
            'CREUSR_0',
            Unicode(5, 'Latin1_General_BIN2'),
            nullable=False,
            default=text("''"),
        )

    @declared_attr
    def updateUser(cls) -> Mapped[str]:
        return mapped_column(
            'UPDUSR_0',
            Unicode(5, 'Latin1_General_BIN2'),
            nullable=False,
            default=text("''"),
        )

    @declared_attr
    def createDatetime(cls) -> Mapped[datetime.datetime]:
        return mapped_column('CREDATTIM_0', DateTime, nullable=False, default=func.now())

    @declared_attr
    def updateDatetime(cls) -> Mapped[datetime.datetime]:
        return mapped_column(
            'UPDDATTIM_0',
            DateTime,
            nullable=False,
            default=func.now(),
            onupdate=func.now(),
        )

    @declared_attr
    def uniqueID(cls) -> Mapped[bytes]:
        return mapped_column('AUUID_0', BINARY(16), nullable=False, default=lambda: uuid.uuid4().bytes)

    @declared_attr
    def updateChanges(cls) -> Mapped[int]:
        return mapped_column('UPDTICK_0', Integer, default=text('((1))'), nullable=False)


class PrimaryKeyMixin:
    """
    Mixin class to add a primary key field to a SQLAlchemy model.
    This mixin adds a ROWID field that is an auto-incrementing numeric value.
    """

    @declared_attr
    def id(cls) -> Mapped[decimal.Decimal]:
        return mapped_column(
            'ROWID',
            Numeric(38, 0),
            Identity(start=1, increment=1),
            primary_key=True,
        )


class CreateUpdateDateMixin:
    """
    Mixin class to add creation and update timestamp fields to a SQLAlchemy model,
    exposing them with Pythonic names (createDate, updateDate) while mapping
    to legacy database column names (CREDAT_0, UPDDAT_0).
    """

    @declared_attr
    def createDate(cls) -> Mapped[datetime.date]:
        return mapped_column('CREDAT_0', DateTime, nullable=False, default=func.now())

    @declared_attr
    def updateDate(cls) -> Mapped[datetime.date]:
        return mapped_column(
            'UPDDAT_0',
            DateTime,
            nullable=False,
            default=func.now(),
            onupdate=func.now(),
        )


class DimensionTypesMixin:
    """
    Mixin class to add dimension type fields to a SQLAlchemy model.
    This mixin adds fields for various dimension types (DIE_0 to DIE_19).
    """

    @declared_attr
    def dimensionType0(cls) -> Mapped[str]:
        return mapped_column(
            'DIE_0',
            Unicode(10, 'Latin1_General_BIN2'),
            nullable=False,
            default=text("''"),
        )

    @declared_attr
    def dimensionType1(cls) -> Mapped[str]:
        return mapped_column(
            'DIE_1',
            Unicode(10, 'Latin1_General_BIN2'),
            nullable=False,
            default=text("''"),
        )

    @declared_attr
    def dimensionType2(cls) -> Mapped[str]:
        return mapped_column(
            'DIE_2',
            Unicode(10, 'Latin1_General_BIN2'),
            nullable=False,
            default=text("''"),
        )

    @declared_attr
    def dimensionType3(cls) -> Mapped[str]:
        return mapped_column(
            'DIE_3',
            Unicode(10, 'Latin1_General_BIN2'),
            nullable=False,
            default=text("''"),
        )

    @declared_attr
    def dimensionType4(cls) -> Mapped[str]:
        return mapped_column(
            'DIE_4',
            Unicode(10, 'Latin1_General_BIN2'),
            nullable=False,
            default=text("''"),
        )

    @declared_attr
    def dimensionType5(cls) -> Mapped[str]:
        return mapped_column(
            'DIE_5',
            Unicode(10, 'Latin1_General_BIN2'),
            nullable=False,
            default=text("''"),
        )

    @declared_attr
    def dimensionType6(cls) -> Mapped[str]:
        return mapped_column(
            'DIE_6',
            Unicode(10, 'Latin1_General_BIN2'),
            nullable=False,
            default=text("''"),
        )

    @declared_attr
    def dimensionType7(cls) -> Mapped[str]:
        return mapped_column(
            'DIE_7',
            Unicode(10, 'Latin1_General_BIN2'),
            nullable=False,
            default=text("''"),
        )

    @declared_attr
    def dimensionType8(cls) -> Mapped[str]:
        return mapped_column(
            'DIE_8',
            Unicode(10, 'Latin1_General_BIN2'),
            nullable=False,
            default=text("''"),
        )

    @declared_attr
    def dimensionType9(cls) -> Mapped[str]:
        return mapped_column(
            'DIE_9',
            Unicode(10, 'Latin1_General_BIN2'),
            nullable=False,
            default=text("''"),
        )

    @declared_attr
    def dimensionType10(cls) -> Mapped[str]:
        return mapped_column(
            'DIE_10',
            Unicode(10, 'Latin1_General_BIN2'),
            nullable=False,
            default=text("''"),
        )

    @declared_attr
    def dimensionType11(cls) -> Mapped[str]:
        return mapped_column(
            'DIE_11',
            Unicode(10, 'Latin1_General_BIN2'),
            nullable=False,
            default=text("''"),
        )

    @declared_attr
    def dimensionType12(cls) -> Mapped[str]:
        return mapped_column(
            'DIE_12',
            Unicode(10, 'Latin1_General_BIN2'),
            nullable=False,
            default=text("''"),
        )

    @declared_attr
    def dimensionType13(cls) -> Mapped[str]:
        return mapped_column(
            'DIE_13',
            Unicode(10, 'Latin1_General_BIN2'),
            nullable=False,
            default=text("''"),
        )

    @declared_attr
    def dimensionType14(cls) -> Mapped[str]:
        return mapped_column(
            'DIE_14',
            Unicode(10, 'Latin1_General_BIN2'),
            nullable=False,
            default=text("''"),
        )

    @declared_attr
    def dimensionType15(cls) -> Mapped[str]:
        return mapped_column(
            'DIE_15',
            Unicode(10, 'Latin1_General_BIN2'),
            nullable=False,
            default=text("''"),
        )

    @declared_attr
    def dimensionType16(cls) -> Mapped[str]:
        return mapped_column(
            'DIE_16',
            Unicode(10, 'Latin1_General_BIN2'),
            nullable=False,
            default=text("''"),
        )

    @declared_attr
    def dimensionType17(cls) -> Mapped[str]:
        return mapped_column(
            'DIE_17',
            Unicode(10, 'Latin1_General_BIN2'),
            nullable=False,
            default=text("''"),
        )

    @declared_attr
    def dimensionType18(cls) -> Mapped[str]:
        return mapped_column(
            'DIE_18',
            Unicode(10, 'Latin1_General_BIN2'),
            nullable=False,
            default=text("''"),
        )

    @declared_attr
    def dimensionType19(cls) -> Mapped[str]:
        return mapped_column(
            'DIE_19',
            Unicode(10, 'Latin1_General_BIN2'),
            nullable=False,
            default=text("''"),
        )


class DimensionMixin:
    """
    Mixin class to add dimension fields to a SQLAlchemy model.
    This mixin adds fields for various dimension types (CCE_0 to CCE_19).
    """

    @declared_attr
    def dimension0(cls) -> Mapped[str]:
        return mapped_column(
            'CCE_0',
            Unicode(15, 'Latin1_General_BIN2'),
            nullable=False,
            default=text("''"),
        )

    @declared_attr
    def dimension1(cls) -> Mapped[str]:
        return mapped_column(
            'CCE_1',
            Unicode(15, 'Latin1_General_BIN2'),
            nullable=False,
            default=text("''"),
        )

    @declared_attr
    def dimension2(cls) -> Mapped[str]:
        return mapped_column(
            'CCE_2',
            Unicode(15, 'Latin1_General_BIN2'),
            nullable=False,
            default=text("''"),
        )

    @declared_attr
    def dimension3(cls) -> Mapped[str]:
        return mapped_column(
            'CCE_3',
            Unicode(15, 'Latin1_General_BIN2'),
            nullable=False,
            default=text("''"),
        )

    @declared_attr
    def dimension4(cls) -> Mapped[str]:
        return mapped_column(
            'CCE_4',
            Unicode(15, 'Latin1_General_BIN2'),
            nullable=False,
            default=text("''"),
        )

    @declared_attr
    def dimension5(cls) -> Mapped[str]:
        return mapped_column(
            'CCE_5',
            Unicode(15, 'Latin1_General_BIN2'),
            nullable=False,
            default=text("''"),
        )

    @declared_attr
    def dimension6(cls) -> Mapped[str]:
        return mapped_column(
            'CCE_6',
            Unicode(15, 'Latin1_General_BIN2'),
            nullable=False,
            default=text("''"),
        )

    @declared_attr
    def dimension7(cls) -> Mapped[str]:
        return mapped_column(
            'CCE_7',
            Unicode(15, 'Latin1_General_BIN2'),
            nullable=False,
            default=text("''"),
        )

    @declared_attr
    def dimension8(cls) -> Mapped[str]:
        return mapped_column(
            'CCE_8',
            Unicode(15, 'Latin1_General_BIN2'),
            nullable=False,
            default=text("''"),
        )

    @declared_attr
    def dimension9(cls) -> Mapped[str]:
        return mapped_column(
            'CCE_9',
            Unicode(15, 'Latin1_General_BIN2'),
            nullable=False,
            default=text("''"),
        )

    @declared_attr
    def dimension10(cls) -> Mapped[str]:
        return mapped_column(
            'CCE_10',
            Unicode(15, 'Latin1_General_BIN2'),
            nullable=False,
            default=text("''"),
        )

    @declared_attr
    def dimension11(cls) -> Mapped[str]:
        return mapped_column(
            'CCE_11',
            Unicode(15, 'Latin1_General_BIN2'),
            nullable=False,
            default=text("''"),
        )

    @declared_attr
    def dimension12(cls) -> Mapped[str]:
        return mapped_column(
            'CCE_12',
            Unicode(15, 'Latin1_General_BIN2'),
            nullable=False,
            default=text("''"),
        )

    @declared_attr
    def dimension13(cls) -> Mapped[str]:
        return mapped_column(
            'CCE_13',
            Unicode(15, 'Latin1_General_BIN2'),
            nullable=False,
            default=text("''"),
        )

    @declared_attr
    def dimension14(cls) -> Mapped[str]:
        return mapped_column(
            'CCE_14',
            Unicode(15, 'Latin1_General_BIN2'),
            nullable=False,
            default=text("''"),
        )

    @declared_attr
    def dimension15(cls) -> Mapped[str]:
        return mapped_column(
            'CCE_15',
            Unicode(15, 'Latin1_General_BIN2'),
            nullable=False,
            default=text("''"),
        )

    @declared_attr
    def dimension16(cls) -> Mapped[str]:
        return mapped_column(
            'CCE_16',
            Unicode(15, 'Latin1_General_BIN2'),
            nullable=False,
            default=text("''"),
        )

    @declared_attr
    def dimension17(cls) -> Mapped[str]:
        return mapped_column(
            'CCE_17',
            Unicode(15, 'Latin1_General_BIN2'),
            nullable=False,
            default=text("''"),
        )

    @declared_attr
    def dimension18(cls) -> Mapped[str]:
        return mapped_column(
            'CCE_18',
            Unicode(15, 'Latin1_General_BIN2'),
            nullable=False,
            default=text("''"),
        )

    @declared_attr
    def dimension19(cls) -> Mapped[str]:
        return mapped_column(
            'CCE_19',
            Unicode(15, 'Latin1_General_BIN2'),
            nullable=False,
            default=text("''"),
        )
