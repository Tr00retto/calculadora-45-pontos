# Quanto falta? · Esporte com Valor

Calculadora de metas com escudos, modo manual e comparação de aproveitamento.

## Atualização automática gratuita

A rotina `.github/workflows/atualizar.yml` consulta a tabela comunitária da Wikipédia uma vez ao dia, às 04h15 UTC (01h15 de Brasília). Também pode ser iniciada em Actions → Atualizar classificação e publicar → Run workflow. Não exige chave ou Secret da API-Sports. O Secret API_FOOTBALL_KEY pode ser removido pelo proprietário, pois não é utilizado.

Em Settings → Pages, Source deve ser GitHub Actions.

O script Python usa somente a biblioteca padrão. Valida os 20 clubes, IDs únicos, pontos, jogos e consistência do total de partidas. Rejeita tabelas que reduzam jogos disputados em relação ao cadastro anterior. Se houver falha, o arquivo e a versão pública anteriores são preservados; a execução fica vermelha no Actions. A interface alerta quando a última consulta válida tem mais de 36 horas.

Uma consulta bem-sucedida não garante que a comunidade atualizou todos os resultados. Não é um serviço em tempo real nem classificação oficial. Mudanças de formato, correções ou punições podem exigir revisão manual. A temporada está fixada em 2026 e deve ser atualizada para o campeonato seguinte.

## Fonte e condições de reutilização

Fonte: https://pt.wikipedia.org/wiki/Campeonato_Brasileiro_de_Futebol_de_2026_-_S%C3%A9rie_A

Histórico/autoria: https://pt.wikipedia.org/w/index.php?title=Campeonato_Brasileiro_de_Futebol_de_2026_-_S%C3%A9rie_A&action=history

Tabela adaptada por extração e normalização dos pontos e jogos, atribuída aos colaboradores da Wikipédia e disponibilizada sob CC BY-SA 4.0: https://creativecommons.org/licenses/by-sa/4.0/ . A atribuição, a indicação de adaptação e a licença também aparecem no rodapé público e nos metadados do JSON. A licença da tabela não licencia os escudos dos clubes nem o código desta aplicação.

Condições de reutilização verificadas nos Termos da Wikimedia: https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use . A rotina faz uma consulta diária identificada por User-Agent, sem login e sem contornar restrições. Não há garantia de disponibilidade ou atualização da fonte.

## Cálculos

Atual = pontos / (3 × jogos disputados). Necessário = máximo(0, meta − pontos) / (3 × jogos restantes). Diferença em pontos percentuais. Os 45 pontos não garantem permanência. A projeção não é previsão nem probabilidade.

Escudos incorporados ao HTML, originalmente fornecidos por API-Sports; pertencem aos respectivos clubes.
