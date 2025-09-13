from enum import Enum
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class NivelAluno(str, Enum):
    """Níveis de conhecimento do aluno"""

    INICIANTE = 'INICIANTE'
    INTERMEDIARIO = 'INTERMEDIARIO'
    AVANCADO = 'AVANCADO'
    EXPERT = 'EXPERT'


class ImpactoAprendizado(str, Enum):
    """Níveis de impacto no aprendizado"""

    BAIXO = 'baixo'
    MEDIO = 'medio'
    ALTO = 'alto'


class ErroDetalhado(BaseModel):
    """Modelo para detalhes de um erro específico"""

    tipo: str = Field(..., description='Tipo específico do erro')
    descricao: str = Field(
        ..., description='Explicação detalhada do erro encontrado'
    )
    correcao_sugerida: str = Field(
        ..., description='Instrução específica de como corrigir o erro'
    )
    impacto_aprendizado: ImpactoAprendizado = Field(
        ..., description='Avaliação do impacto no aprendizado'
    )


class ErrosPorCategoria(BaseModel):
    """Categorização de erros encontrados no código"""

    sintaticos: List[ErroDetalhado] = Field(
        default_factory=list,
        description='Erros de sintaxe que impedem a execução do código',
    )
    logicos: List[ErroDetalhado] = Field(
        default_factory=list,
        description='Erros de lógica que fazem o código produzir resultados incorretos',
    )
    estruturais: List[ErroDetalhado] = Field(
        default_factory=list,
        description='Problemas na organização e estrutura do código',
    )
    performance: List[ErroDetalhado] = Field(
        default_factory=list,
        description='Questões relacionadas à eficiência e otimização do código',
    )
    boas_praticas: List[ErroDetalhado] = Field(
        default_factory=list,
        description='Violações das convenções e melhores práticas da linguagem',
    )


class AnaliseGeral(BaseModel):
    """Avaliação geral do nível técnico e contexto do código"""

    nivel_aluno: NivelAluno = Field(
        ..., description='Classificação do nível de conhecimento do aluno'
    )
    linguagem_programacao: str = Field(
        ..., description='Linguagem de programação identificada'
    )
    objetivo_codigo: str = Field(
        ..., description='Descrição do que o código deveria fazer'
    )
    topicos_envolvidos: List[str] = Field(
        ..., description='Conceitos de programação identificados'
    )
    pontuacao_geral: int = Field(
        ...,
        ge=0,
        le=100,
        description='Pontuação geral considerando funcionalidade, qualidade e boas práticas',
    )


class DiagnosticoErros(BaseModel):
    """Análise detalhada de todos os tipos de erros encontrados"""

    total_erros: int = Field(
        ..., ge=0, description='Quantidade total de erros identificados'
    )
    erros_por_categoria: ErrosPorCategoria = Field(
        ..., description='Erros categorizados por tipo'
    )


class FeedbackConstrutivo(BaseModel):
    """Feedback educacional focado no desenvolvimento do aluno"""

    pontos_fortes: List[str] = Field(
        ...,
        description='Aspectos positivos identificados para reforçar o aprendizado',
    )
    areas_melhoria: List[str] = Field(
        ...,
        description='Áreas específicas para desenvolvimento das habilidades',
    )
    proximos_passos: List[str] = Field(
        ..., description='Sugestões concretas de estudo para o próximo nível'
    )
    recursos_recomendados: List[str] = Field(
        ...,
        description='Materiais de estudo específicos relacionados aos tópicos',
    )


class CodigoMelhorado(BaseModel):
    """Versão otimizada do código com correções e melhorias"""

    incluir: bool = Field(
        ..., description='Variável que determina se incluir código corrigido'
    )
    versao_corrigida: Optional[str] = Field(
        None, description='Código completo com todas as correções aplicadas'
    )
    explicacao_mudancas: str = Field(
        ...,
        description='Explicação educacional detalhada de cada mudança feita',
    )


class AnaliseCodigoCompleta(BaseModel):
    """Modelo principal para análise completa de código de estudante"""

    analise_geral: AnaliseGeral = Field(
        ..., description='Avaliação geral do código'
    )
    diagnostico_erros: DiagnosticoErros = Field(
        ..., description='Análise detalhada de erros'
    )
    feedback_construtivo: FeedbackConstrutivo = Field(
        ..., description='Feedback educacional'
    )
    codigo_melhorado: CodigoMelhorado = Field(
        ..., description='Versão otimizada do código'
    )


# Modelo alternativo mais simples para casos específicos
class AnaliseRapida(BaseModel):
    """Modelo simplificado para análises rápidas"""

    nivel_aluno: NivelAluno
    linguagem: str
    total_erros: int = Field(ge=0)
    pontuacao: int = Field(ge=0, le=100)
    principais_problemas: List[str]
    sugestoes: List[str]


# Modelos auxiliares para validações específicas
class ConfigAnalise(BaseModel):
    """Configurações para personalizar a análise"""

    incluir_codigo_corrigido: bool = True
    nivel_detalhamento: Literal['basico', 'completo', 'avancado'] = 'completo'
    focar_em_categoria: Optional[str] = None
    linguagem_esperada: Optional[str] = None
