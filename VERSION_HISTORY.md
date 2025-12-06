# Histórico de Versões do BigodeTexas Bot

## Site 9.3 (06/12/2025) 🚀

**Tag:** `site-9.3-2025-12-06`

**Principais Mudanças:**

- **Novas Funcionalidades:** Implementação completa de Base, Clã e Banco Sul no painel web.
- **Banco de Dados:** Schema adaptativo (`schema_v2_compat.sql`) com suporte a bases e clãs.
- **Interfaces:** Templates `base.html`, `clan.html` e `banco.html` integrados e funcionais.
- **API:** Rotas para registro de base, criação de clã e transferências bancárias.
- **Backups:** Scripts de backup e diagnósticos aprimorados.

## Site 9.2 (30/11/2025) 🎨

**Tag:** `site-9.2-2025-11-30`

**Principais Mudanças:**

- **Checkout Navbar:** Substituído header customizado por navbar padrão com logo Texas.
- **Heatmap Fallback:** Adicionado fundo de grid quando tiles do iZurvive não carregam.
- **Bug Fixes:** Corrigidos erros de sintaxe CSS e warnings de markdown.
- **UX:** Visual consistente em todas as páginas do site.

## Site 9.1 (30/11/2025) 🔥

**Tag:** `site-9.1-2025-11-30`

**Principais Mudanças:**

- **Arquitetura Completa do ChatGPT:** Implementação 100% da arquitetura sugerida para Heatmap PvP.
- **Parser de Logs RPT:** Função `parse_rpt_line()` com suporte a múltiplos formatos.
- **API `/api/parse_log`:** Endpoint para receber logs via POST e salvar no banco.
- **Integração Nitrado:** Script `nitrado_to_heatmap.py` que lê logs via FTP automaticamente.
- **Grid Clustering:** Agregação inteligente de dados para performance.
- **Documentação:** Guia completo (`HEATMAP_GUIDE.md`) e script de testes.
- **Backend Real:** Dados reais do banco SQLite (não mais hardcoded).

## Projeto 9 (29/11/2025)

**Tag:** `projeto-9-2025-11-29`

**Principais Mudanças:**

- **Novo Recurso:** Mapa de Calor (Heatmap) PvP inspirado no concorrente.
- **Melhoria:** Integração de mapa iZurvive no Checkout.
- **Visual:** Backgrounds personalizados (DayZ) e correções de CSS.
- **Correção:** Página de confirmação de pedido funcionando.

## Versões Anteriores

- ...
