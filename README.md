# Quanto falta? · Esporte com Valor

Calculadora estática, sem dependências de instalação, para comparar aproveitamento atual e necessário para uma meta de pontos.

## Publicar

No GitHub, abra Settings → Pages. Em Build and deployment, escolha Deploy from a branch, branch `main`, pasta `/ (root)` e Save. Após a publicação, o endereço esperado é https://Tr00retto.github.io/calculadora-45-pontos/ .

## Recursos

- Seleção por escudo dos 20 clubes; pontos e jogos preenchidos a partir do cadastro.
- Entrada manual e meta configurável.
- Aproveitamento, diferença em pontos percentuais, pontos restantes, máximo e projeção matemática.
- Estados de meta alcançada, impossível e início/fim do campeonato.
- Layout responsivo azul-escuro e dourado.

## Atualizar dados

Edite o array `clubs` no final de `index.html`. Cada registro contém `[nome, pontos, jogos disputados, identificador da imagem API-Sports]`. Atualize também a data e fonte no rodapé e no texto de `origin`. O cadastro inicial é uma fotografia de 17/10/2026, 00h45, da página https://classificacaogeral.com.br/campeonato-brasileiro-serie-a/2026 . Não há atualização automática nem consulta ao vivo. Alterações pelo leitor são apenas simulações na página e não alteram o cadastro compartilhado.

As imagens externas dependem da disponibilidade do provedor. Os nomes permanecem acessíveis se as imagens falharem. Escudos pertencem aos respectivos clubes.

## Método

Atual = pontos / (3 × jogos). Necessário = máximo(0, meta − pontos) / (3 × jogos restantes). Diferença = necessário − atual, em pontos percentuais. A referência de 45 pontos não garante permanência. A projeção não é uma previsão ou probabilidade.

## Validação

Sintaxe JavaScript e oito verificações de cálculo: cenário 32 pontos/31 jogos, meta alcançada, campeonato encerrado, nenhum jogo, meta impossível, pontos incompatíveis com jogos, jogos acima do total e entrada fracionária.
