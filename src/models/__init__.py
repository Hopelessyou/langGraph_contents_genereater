"""데이터 모델 정의"""

from .base import BaseDocument
from .statute import StatuteModel, StatuteMetadata
from .case import CaseModel, CaseMetadata
from .procedure import ProcedureModel, ProcedureMetadata
from .template import TemplateModel, TemplateMetadata
from .manual import ManualModel, ManualMetadata
from .case_type import CaseTypeModel, CaseTypeMetadata
from .sentencing_guideline import SentencingGuidelineModel, SentencingGuidelineMetadata
from .faq import FAQModel, FAQMetadata
from .keyword_mapping import KeywordMappingModel, KeywordMappingMetadata
from .style_issue import StyleIssueModel, StyleIssueMetadata
from .statistics import StatisticsModel, StatisticsMetadata

__all__ = [
    "BaseDocument",
    "StatuteModel",
    "StatuteMetadata",
    "CaseModel",
    "CaseMetadata",
    "ProcedureModel",
    "ProcedureMetadata",
    "TemplateModel",
    "TemplateMetadata",
    "ManualModel",
    "ManualMetadata",
    "CaseTypeModel",
    "CaseTypeMetadata",
    "SentencingGuidelineModel",
    "SentencingGuidelineMetadata",
    "FAQModel",
    "FAQMetadata",
    "KeywordMappingModel",
    "KeywordMappingMetadata",
    "StyleIssueModel",
    "StyleIssueMetadata",
    "StatisticsModel",
    "StatisticsMetadata",
]
