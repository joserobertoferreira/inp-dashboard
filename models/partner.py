from typing import List, Optional

from sqlalchemy import (
    Index,
    Integer,
    PrimaryKeyConstraint,
    SmallInteger,
    Unicode,
    text,
)
from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column

from core.base import Base
from core.generics_mixins import ArrayColumnMixin
from core.mixins import AuditMixin, CreateUpdateDateMixin, PrimaryKeyMixin


class Partner(
    Base,
    AuditMixin,
    PrimaryKeyMixin,
    CreateUpdateDateMixin,
):
    __tablename__ = 'BPARTNER'
    __table_args__ = (
        PrimaryKeyConstraint('ROWID', name='BPARTNER_ROWID'),
        Index('BPARTNER_BPR0', 'BPRNUM_0', unique=True),
        Index('BPARTNER_BPR1', 'BPRSHO_0'),
        Index('BPARTNER_BPR2', 'BETFCY_0', 'FCY_0', 'BPRNUM_0', unique=True),
    )

    bp: Mapped[str] = mapped_column('BPRNUM_0', Unicode(15, 'Latin1_General_BIN2'), server_default=text("''"))
    isActive: Mapped[int] = mapped_column('ENAFLG_0', TINYINT, server_default=text('((2))'))
    category: Mapped[str] = mapped_column('BRGCOD_0', Unicode(5, 'Latin1_General_BIN2'), server_default=text("''"))
    customerOrSupplier: Mapped[str] = mapped_column(
        'BRGOBJ_0', Unicode(3, 'Latin1_General_BIN2'), server_default=text("''")
    )

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='BPRNAM',
        property_name='partnerName',
        count=2,
        column_type=Unicode(35, 'Latin1_General_BIN2'),
        python_type=str,
        server_default=text("''"),
    )

    partnerNames: Mapped[List[Optional[str]]] = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    shortName: Mapped[str] = mapped_column('BPRSHO_0', Unicode(10, 'Latin1_General_BIN2'), server_default=text("''"))
    europeanVatNumber: Mapped[str] = mapped_column(
        'EECNUM_0', Unicode(20, 'Latin1_General_BIN2'), server_default=text("''")
    )
    isInterSite: Mapped[int] = mapped_column('BETFCY_0', TINYINT, server_default=text('((1))'))
    businessPartnerSite: Mapped[str] = mapped_column(
        'FCY_0', Unicode(5, 'Latin1_General_BIN2'), server_default=text("''")
    )
    country: Mapped[str] = mapped_column('CRY_0', Unicode(3, 'Latin1_General_BIN2'), server_default=text("''"))
    siteIDNumber: Mapped[str] = mapped_column('CRN_0', Unicode(20, 'Latin1_General_BIN2'), server_default=text("''"))
    standardIndustrialClassificationCode: Mapped[str] = mapped_column(
        'NAF_0', Unicode(1, 'Latin1_General_BIN2'), server_default=text("''")
    )
    currency: Mapped[str] = mapped_column('CUR_0', Unicode(3, 'Latin1_General_BIN2'), server_default=text("''"))
    language: Mapped[str] = mapped_column('LAN_0', Unicode(3, 'Latin1_General_BIN2'), server_default=text("''"))
    acronym: Mapped[str] = mapped_column('BPRLOG_0', Unicode(10, 'Latin1_General_BIN2'), server_default=text("''"))
    italianTaxNumber: Mapped[str] = mapped_column(
        'VATNUM_0', Unicode(1, 'Latin1_General_BIN2'), server_default=text("''")
    )
    fiscalCode: Mapped[str] = mapped_column('FISCOD_0', Unicode(1, 'Latin1_General_BIN2'), server_default=text("''"))
    consolidationGroup: Mapped[str] = mapped_column(
        'GRUGPY_0', Unicode(5, 'Latin1_General_BIN2'), server_default=text("''")
    )
    consolidationCode: Mapped[str] = mapped_column(
        'GRUCOD_0', Unicode(1, 'Latin1_General_BIN2'), server_default=text("''")
    )
    isCustomer: Mapped[int] = mapped_column('BPCFLG_0', TINYINT, server_default=text('((1))'))
    isSupplier: Mapped[int] = mapped_column('BPSFLG_0', TINYINT, server_default=text('((1))'))
    isGrantor: Mapped[int] = mapped_column('CCNFLG_0', SmallInteger, server_default=text('((0))'))
    isCarrier: Mapped[int] = mapped_column('BPTFLG_0', TINYINT, server_default=text('((1))'))
    isFactor: Mapped[int] = mapped_column('FCTFLG_0', TINYINT, server_default=text('((1))'))
    isSalesRep: Mapped[int] = mapped_column('REPFLG_0', TINYINT, server_default=text('((1))'))
    isMiscellaneousBP: Mapped[int] = mapped_column('BPRACC_0', TINYINT, server_default=text('((1))'))
    isProspect: Mapped[int] = mapped_column('PPTFLG_0', TINYINT, server_default=text('((1))'))
    isServiceSupplier: Mapped[int] = mapped_column('PRVFLG_0', TINYINT, server_default=text('((1))'))
    isServiceCaller: Mapped[int] = mapped_column('DOOFLG_0', TINYINT, server_default=text('((1))'))
    accountingCode: Mapped[str] = mapped_column(
        'ACCCOD_0', Unicode(10, 'Latin1_General_BIN2'), server_default=text("''")
    )
    isShipTo: Mapped[int] = mapped_column('PTHFLG_0', SmallInteger, server_default=text('((0))'))

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='BPRFLG',
        property_name='miscellaneousFlag',
        count=4,
        column_type=TINYINT,
        python_type=int,
        server_default=text('((1))'),
    )

    miscellaneous: Mapped[List[Optional[int]]] = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    defaultAddress: Mapped[str] = mapped_column(
        'BPAADD_0', Unicode(5, 'Latin1_General_BIN2'), server_default=text("''")
    )
    defaultContact: Mapped[str] = mapped_column(
        'CNTNAM_0', Unicode(35, 'Latin1_General_BIN2'), server_default=text("''")
    )
    defaultBankId: Mapped[str] = mapped_column(
        'BIDNUM_0', Unicode(30, 'Latin1_General_BIN2'), server_default=text("''")
    )
    bankIdCountry: Mapped[str] = mapped_column('BIDCRY_0', Unicode(3, 'Latin1_General_BIN2'), server_default=text("''"))
    reportAccessCode: Mapped[str] = mapped_column(
        'ACS_0', Unicode(10, 'Latin1_General_BIN2'), server_default=text("''")
    )
    exportNumber: Mapped[int] = mapped_column('EXPNUM_0', Integer, server_default=text('((0))'))
    expenseEntryType: Mapped[str] = mapped_column(
        'BPRGTETYP_0', Unicode(5, 'Latin1_General_BIN2'), server_default=text("''")
    )
    isMailingProhibited: Mapped[int] = mapped_column('BPRFBDMAG_0', TINYINT, server_default=text('((1))'))
    cfonbPaymentMethod: Mapped[str] = mapped_column(
        'MODPAM_0', Unicode(20, 'Latin1_General_BIN2'), server_default=text("''")
    )
    nonResidentAccount: Mapped[str] = mapped_column(
        'ACCNONREI_0', Unicode(5, 'Latin1_General_BIN2'), server_default=text("''")
    )
    isPhysicalPerson: Mapped[int] = mapped_column('LEGETT_0', TINYINT, server_default=text('((1))'))
    isCashExcluded: Mapped[int] = mapped_column('CFOEXD_0', TINYINT, server_default=text('((1))'))
    documentType: Mapped[int] = mapped_column('DOCTYP_0', SmallInteger, server_default=text('((0))'))
    isPublicSector: Mapped[int] = mapped_column('BPPFLG_0', TINYINT, server_default=text('((1))'))
    relatedCompany: Mapped[int] = mapped_column('CPYREL_0', TINYINT, server_default=text('((1))'))
    consolidationPartner: Mapped[str] = mapped_column(
        'CSLBPR_0', Unicode(1, 'Latin1_General_BIN2'), server_default=text("''")
    )
    registrationNumber: Mapped[str] = mapped_column(
        'REGNUM_0', Unicode(1, 'Latin1_General_BIN2'), server_default=text("''")
    )
    vatNumber: Mapped[str] = mapped_column('VATNO_0', Unicode(1, 'Latin1_General_BIN2'), server_default=text("''"))
    isPaymentItem: Mapped[int] = mapped_column('ZPAGITM_0', TINYINT, server_default=text('((1))'))
    economicOperatorRegistrationAndIdNumber: Mapped[str] = mapped_column(
        'EORINUM_0', Unicode(35, 'Latin1_General_BIN2'), server_default=text("''")
    )
    serviceCode: Mapped[str] = mapped_column(
        'INTSRVCOD_0', Unicode(1, 'Latin1_General_BIN2'), server_default=text("''")
    )
    isEditor: Mapped[int] = mapped_column('ZEDITOR_0', TINYINT, server_default=text('((1))'))
    routingCode: Mapped[str] = mapped_column('RTGCOD_0', Unicode(1, 'Latin1_General_BIN2'), server_default=text("''"))
    invoiceType: Mapped[int] = mapped_column('EINVTYP_0', SmallInteger, server_default=text('((0))'))
    isVaspInterface: Mapped[int] = mapped_column('ZINTVSP_0', TINYINT, server_default=text('((1))'))
    invoicingMappingCode: Mapped[str] = mapped_column(
        'MAPCOD_0', Unicode(1, 'Latin1_General_BIN2'), server_default=text("''")
    )
    isAgent: Mapped[int] = mapped_column('ZAGENTE_0', TINYINT, server_default=text('((1))'))
    isManager: Mapped[int] = mapped_column('ZGESFLG_0', TINYINT, server_default=text('((1))'))
    isAnalyst: Mapped[int] = mapped_column('ZANAFLG_0', TINYINT, server_default=text('((1))'))
    isExporter: Mapped[int] = mapped_column('ZEXPFLG_0', TINYINT, server_default=text('((1))'))
