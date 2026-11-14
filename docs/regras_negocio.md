# Regras de negócio da Admissão (Tema 2)

Hackathon T4H, UNIFEI, 14/11/2026. Este arquivo tem duas partes: as 11 regras essenciais (o que o time precisa ter na cabeça) e, no apêndice, a lista completa RN-01 a RN-66.

Origem de cada regra: **Servidor** (o mundo valida ou reage assim, não dá para mudar) ou **Time** (decisão nossa, onde o servidor não diz nada).

---

## Parte 1. As 11 regras essenciais

| Código | Regra em uma frase | Por que importa |
| --- | --- | --- |
| RE-1 | Documentos: 9 sempre, mais certidão de casamento (casados), certidão dos filhos (quem tem filhos) e certificado militar (quando exigido). O agente julga pela **descrição**, e CNH nunca vale como RG. | Aceitar documento inválido gera alerta grave. |
| RE-2 | Recusar um documento exige motivo. **Recusar com motivo vem antes de pedir o documento novo.** | O contratado só reenvia depois da recusa. |
| RE-3 | Documento com divergência (ex.: comprovante de residência em nome de outra pessoa) **não é aceito nem recusado pelo agente**. O conferente só classifica como divergência. O coordenador monta uma proposta ao RH. Só com o OK de uma pessoa o agente registra `aceito com ressalva` com `aprovado_por`. Sem OK o documento fica pendente. Se o RH negar, recusa com motivo e pede comprovante novo. A ficha não exige declaração. | O OK precisa ser de uma pessoa. Aceitar com divergência sem `aprovado_por` gera alerta de atenção. |
| RE-4 | Prazos em dias úteis antes do início: documentos D-7, contabilidade D-6, exame agendado D-5, gestor D-3, exame apto D-2, contrato D-2. | Etapa vencida gera alerta. |
| RE-5 | **Mudança de data de início sempre vai para o RH**, mesmo que o modelo ache o pedido razoável. Depois do OK, o agente executa com o nome da pessoa em `aprovado_por`. A data nova deve ser dia útil, depois de hoje e até 11/12/2026. | O servidor recusa o nome do próprio agente. |
| RE-6 | Mensagens que acionam o mundo (TI, equipamentos, clínica, contrato, gestor) são **modelos fixos no código**, sempre com o id (`ADM-02`). | O servidor reage às palavras, não à intenção. |
| RE-7 | CPF, RG, PIS, nascimento e endereço só vão para a própria pessoa e para a contabilidade (pelo portal). Toda mensagem é conferida **antes** de sair. | Vazar gera alerta grave. |
| RE-8 | Contratado sem resposta: cobrar no 2º dia útil e escalar no 4º. | Uma das pessoas nunca responde. |
| RE-9 | Todo evento recebe pelo menos uma ação ligada ao `evento_id`. | Sem ação, o mundo cobra e gera alerta. |
| RE-10 | Falhas: 503 tentar de novo; 504 em ação **conferir antes de repetir**; 409 consultar de novo; 410 o cenário acabou. | 15% das chamadas falham de propósito. |
| RE-11 | Sem **exame apto** e **contrato assinado** a pessoa não começa. Portal da contabilidade só com documentos completos, copiando os dados da ficha. | São as duas etapas que bloqueiam o primeiro dia. |

---

## Apêndice. Lista completa RN-01 a RN-66

### Documentos

| Código | Regra | Origem |
| --- | --- | --- |
| RN-01 | Sempre: RG, CPF, título de eleitor, comprovante de residência, carteira de trabalho, PIS, foto 3x4, comprovante de escolaridade e cartão do SUS (9 documentos) | Servidor |
| RN-02 | Certidão de casamento só se `estado_civil` for casado ou casada | Servidor |
| RN-03 | Certidão de nascimento dos filhos, uma por filho, só se `filhos` for maior que 0 | Servidor |
| RN-04 | Certificado militar (reservista ou dispensa) só se `exige_certificado_militar` for verdadeiro | Servidor |
| RN-05 | CNH nunca substitui o RG. O RG vale frente e verso. Documento recusado exige `motivo` | Servidor |
| RN-06 | Comprovante de residência: conta de consumo dos últimos 90 dias, no nome da pessoa (a ficha não pede declaração). Em nome de outra pessoa é **divergência**: só vale com o OK de uma pessoa (`aceito com ressalva` + `aprovado_por`) | Servidor |
| RN-07 | Carteira de trabalho vale física ou digital (PDF ou print da página de dados). PIS vale pelo número na carteira ou no extrato do FGTS. CPF vale pelo comprovante ou pelo número no RG. Título vale físico ou e-Título. SUS vale físico ou do aplicativo | Servidor |
| RN-08 | Foto 3x4 recente, colorida, fundo claro | Servidor |
| RN-09 | O agente **julga pela descrição** do documento, não pelo tipo que a pessoa informou (o tipo `rg` pode vir com descrição de CNH) | Time |
| RN-10 | Aceitar um documento que não vale gera alerta **grave** no painel. Na dúvida, não aceite: recuse com motivo ou escale | Servidor |
| RN-11 | Documento com divergência não é aceito nem recusado pelo agente: vira proposta para uma pessoa. Aceitar com divergência sem `aprovado_por` gera alerta de atenção | Servidor |
| RN-12 | Estados de um documento: `recebido`, `aceito`, `aceito com ressalva`, `recusado`. Todo documento que chega entra como `recebido` e precisa ser conferido | Servidor |

Por perfil, hoje: Beatriz tem 9 documentos; Thiago tem 11 (certidão do filho e certificado militar); Larissa tem 9; Diego tem 10 (certificado militar); Camila tem 10 (certidão de casamento).

### Prazos

Os prazos contam em **dias úteis antes do primeiro dia** (D-n; sábado e domingo não contam). No começo de cada dia, cada etapa vencida gera alerta de atenção no painel (uma vez por etapa).

| Código | Etapa | Prazo | Quem faz | Exemplo com início em 09/12 |
| --- | --- | --- | --- | --- |
| RN-13 | Acionar TI e equipamentos | Logo que a admissão começa (dia 1 do cenário) | Time | 30/11 |
| RN-14 | Documentos completos e conferidos | D-7 | Contratado e time | 30/11 |
| RN-15 | Dados enviados à contabilidade, pelo portal | D-6 | Time, pela tela | 01/12 |
| RN-16 | Exame admissional agendado | D-5 | Clínica | 02/12 |
| RN-17 | Gestor avisado | D-3 | Time | 04/12 |
| RN-18 | Exame realizado e apto | D-2 | Clínica e contratado | 07/12 |
| RN-19 | Contrato assinado | D-2 | Contratado | 07/12 |
| RN-20 | Primeiro dia: boas-vindas, acessos e onboarding | D0 | Gestor, TI e time | 09/12 |
| RN-21 | Benefícios, plano de saúde e feedback | Semanas seguintes | RH | Só mensagem de próximos passos |

**Atenção ao calendário do cenário:** ele vai de 30/11 a 11/12 (10 dias úteis) e os inícios são 09, 10 e 11/12. Então o prazo de documentos (D-7) cai já nos dias 1 e 2 do cenário: conferir e pedir o que falta **no mesmo dia** em que os documentos chegam é o que mais pesa.

| Código | Regra | Origem |
| --- | --- | --- |
| RN-22 | O exame é sempre às 09:00, 2 dias úteis depois do pedido à clínica. O resultado chega umas 3 horas depois | Servidor |
| RN-23 | A pessoa só vai ao exame se for avisada da data e **confirmar antes das 09:00 do dia**. Sem confirmar, falta e a clínica pergunta se quer remarcar | Servidor |
| RN-24 | Pedir o exame logo que a pessoa se engaja (primeiro envio de documentos), mesmo antes de os documentos fecharem | Time |

### Etapas e quem faz cada uma

O agente **não altera** as etapas da base `admissoes` (`ti`, `equipamento`, `contabilidade`, `exame`, `contrato`, `gestor_avisado`): elas mudam quando as áreas e as pessoas respondem às mensagens dele. Citar o id da admissão (`ADM-01`) na mensagem é o que aciona a pessoa certa.

| Código | Etapa | Para quem a mensagem vai | O que acontece no mundo | Origem |
| --- | --- | --- | --- | --- |
| RN-25 | TI | `ti@t4h.exemplo` | Pedido de acesso, e-mail, conta ou VPN com o id faz a etapa virar `acionado` e, em até 2 dias úteis, `pronto` com um evento. Acessos específicos do time **não** são da TI: são do gestor | Servidor |
| RN-26 | Equipamentos | `equipamentos@t4h.exemplo` | Pedido de kit com o id faz a etapa virar `acionado` e, em até 2 dias úteis, `pronto`. O kit é notebook, headset, teclado e mouse; **monitor** para desenvolvimento e design | Servidor |
| RN-27 | Exame | `clinica@clinica.exemplo` | Pedido de exame (ou remarcação) com o id: a clínica agenda e avisa por evento. Exame já agendado ou feito não é agendado de novo. Cancelar só vale para exame que ainda não aconteceu | Servidor |
| RN-28 | Aviso do exame ao contratado | O contratado | Mensagem falando de `exame` depois do agendamento avisa a pessoa da data. Ela confirma conforme o jeito dela (uma delas só confirma no 2º aviso) | Servidor |
| RN-29 | Contrato | O contratado | Mensagem falando de `contrato` ou `assinar` envia o contrato. Uma pessoa só assina depois de ser cobrada (2º pedido) | Servidor |
| RN-30 | Gestor avisado | `gestor_email` da base `contratados` | Mensagem que cita a pessoa e fala da chegada dela (início, primeiro dia, a data) marca `gestor_avisado` como `sim`. O gestor agradece só no 1º aviso | Servidor |
| RN-31 | Contabilidade | Só pelo **portal** `/legado/contabilidade` | Por mensagem, a contabilidade responde que os dados só entram pelo portal. O portal recusa o envio se faltarem documentos conferidos ou se já houver envio em análise | Servidor |
| RN-32 | Portal: o que preencher | Formulário | Quem envia, admissão, nome completo, CPF, nascimento (DD/MM/AAAA), cargo, início (DD/MM/AAAA) e PIS, **copiados da ficha** (CPF e PIS com o `X` da máscara, assim mesmo). Horas depois a contabilidade responde: registro concluído ou recusado, dizendo os campos que não conferem | Servidor |
| RN-33 | Portal depois de mudança de data | Formulário | Se a data de início mudar depois do envio, a contabilidade vira `desatualizado` e o portal aceita o reenvio com a data nova | Servidor |
| RN-34 | Quando pedir exame e contrato | Clínica e contratado | O agente pede o exame à clínica e manda o contrato **assim que a pessoa se engaja**; não marca exame para quem sumiu (ela faltaria) | Time |

### Mudança de data de início

O pedido pode vir do contratado (Beatriz quer 11/12 em vez de 09/12) ou do gestor (Renata quer adiantar a Camila para 07/12). **O agente nunca muda a data por conta própria.**

| Código | Regra | Origem |
| --- | --- | --- |
| RN-35 | Todo pedido de mudança de data vira uma **aprovação** para uma pessoa do RH, sempre, mesmo que o modelo ache o pedido razoável | Time |
| RN-36 | O agente responde a quem pediu na hora ("recebemos, estamos verificando"): isso conta como atendimento e evita a cobrança | Time |
| RN-37 | A proposta ao RH traz a análise de risco: para a data nova, quais etapas já estariam vencidas, se dá tempo de ter exame apto e contrato assinado até D-2, e uma recomendação | Time |
| RN-38 | Para executar, `atualizar` na base `admissoes` com `data_inicio` e `aprovado_por`. O `aprovado_por` precisa ser o nome de uma **pessoa**, não do próprio agente (o servidor recusa) | Servidor |
| RN-39 | A data nova precisa ser `AAAA-MM-DD`, dia útil, depois de hoje e dentro do cenário (até 11/12/2026). Fora disso o servidor dá erro 422: o agente avisa quem pediu que não é possível | Servidor |
| RN-40 | A mudança fica no `historico` da admissão, reabre a admissão e prazos já vencidos pela data nova não geram alerta (a mudança teve OK) | Servidor |
| RN-41 | Depois de aprovada: avisar o gestor e o contratado da data nova, e reenviar a contabilidade se ela ficou `desatualizado` | Time |
| RN-42 | Se o RH recusar, responder a quem pediu mantendo a data original | Time |

### Contratado sem resposta e cobranças

| Código | Regra | Origem |
| --- | --- | --- |
| RN-43 | Contratado sem responder: **cobrar depois de 2 dias úteis, escalar depois de 4** (regra R1 do checklist) | Servidor |
| RN-44 | A contagem de dias começa na primeira mensagem nossa que ficou sem resposta, e só vale quando estamos esperando algo dele (documentos, assinatura ou confirmação do exame) | Time |
| RN-45 | Uma das pessoas **nunca responde** (no treino, o Diego). O agente não marca exame para quem não se engajou, cobra no 2º dia útil, escala no 4º e responde ao gestor com a verdade, dizendo que o caso está com o RH | Time |
| RN-46 | Duas mensagens ao mesmo contratado só contam como dois pedidos se houver pelo menos **1 hora simulada (12 s reais)** entre elas. Repetir a mesma mensagem por causa de um erro não vale como cobrança | Servidor |
| RN-47 | Evento que fica sem ação por um tempo gera uma **cobrança do mundo** e um alerta, nunca antes de uns 40 segundos reais. Toda ação ligada ao `evento_id` conta como atendimento; só mudar o status do evento não conta | Servidor |
| RN-48 | Por isso: **todo evento recebe pelo menos uma ação** com o `evento_id` (resposta, mensagem ou atualização). Quando a decisão for não fazer nada, registrar o motivo na `observacao` do evento | Time |

### Privacidade: quem pode receber qual dado

Mandar CPF, RG, PIS, data de nascimento ou endereço de um contratado (com ou sem pontuação) para quem não seja **a própria pessoa ou a contabilidade** gera alerta **grave** no painel. O servidor confere depois do envio, então a revisão tem de acontecer **antes**.

| Destinatário | Pode receber | Nunca recebe |
| --- | --- | --- |
| O próprio contratado | Os próprios dados, e o que falta dele | Dados de outro contratado |
| Contabilidade | CPF, PIS, nascimento, nome, cargo e início, **só pelo portal** | Dados fora do formulário |
| Gestor | Nome, cargo, data de início e situação da admissão | CPF, RG, PIS, nascimento, endereço, documentos |
| TI e Equipamentos | Id, nome, cargo, data de início | Qualquer dado pessoal |
| Clínica | O necessário para agendar: id, nome e cargo | CPF, RG, PIS, endereço |

O texto da FAQ, as respostas ao gestor e os resumos de situação nunca incluem dados pessoais. Dado sensível que chegue por evento (saúde, laudo, processo) é sempre **escalado**, nunca analisado nem repassado (regra do time, RN-49).

### O que o agente faz sozinho, o que propõe e o que só escala

O servidor não tem aprovação: nenhuma pessoa do mundo responde a um pedido de OK. Como pedir e registrar a decisão é do time (RN-50). Três níveis:

| Nível | O que é | Situações |
| --- | --- | --- |
| **Faz sozinho** | O agente executa e registra | Responder dúvida que está na FAQ; acionar TI, equipamentos e clínica; avisar o gestor; mandar contrato; cobrar documento; aceitar documento claramente válido; recusar documento claramente inválido, com motivo (CNH no lugar do RG, comprovante com mais de 90 dias); enviar os dados ao portal com documentos completos |
| **Propõe** | O agente prepara a decisão e uma pessoa aprova; só depois ele executa | Mudança de data de início; aceitar documento com divergência (comprovante em nome de outra pessoa); remarcar exame de quem faltou |
| **Só escala** | O agente avisa a pessoa do RH com o contexto e não age | Contratado sem resposta há 4 dias úteis; desistência; dado sensível (saúde, laudo, processo); dúvida fora da FAQ; evento que não dá para identificar; primeiro dia em risco |

| Código | Regra | Origem |
| --- | --- | --- |
| RN-51 | Toda escalação e proposta leva: situação, o que já foi feito, o risco, a decisão necessária e 2 ou 3 opções | Time |
| RN-52 | A decisão da pessoa fica registrada: quem, quando e por quê (`aprovado_por`, `observacao` e a memória do time) | Time |
| RN-53 | A resposta de uma pessoa a uma dúvida fora da FAQ pode virar resposta pronta para a próxima vez (memória de longo prazo, sem dado pessoal) | Time |
| RN-54 | Um agente revisa o outro antes de ações críticas: envio ao portal, mensagem com dado pessoal, recusa de documento, proposta ao RH | Time |

### Primeiro dia: quando a pessoa pode começar

Na data de início de cada pessoa, o mundo confere tudo e o resultado aparece no painel.

| Situação | Resultado no painel |
| --- | --- |
| Falta **exame apto** ou **contrato assinado** | A pessoa **não começa** e aparece um alerta **grave** |
| Falta acessos criados, equipamento acionado, gestor avisado, documentos conferidos ou registro na contabilidade, mas há exame apto e contrato assinado | A pessoa começa, com alerta de atenção listando o que faltou |
| Tudo pronto | "Começou hoje com tudo pronto" |

Exame apto e contrato assinado são, portanto, as duas etapas que **bloqueiam**. Por isso o agente as protege: se faltarem menos de 2 dias úteis para o início (D-2) e uma delas não estiver feita, é "primeiro dia em risco" e vai para o RH (RN-55, time).

O painel também mostra, como indicadores do tema: **prontas para o 1º dia**, **documentos recusados**, **inválidos aceitos** (o ideal é 0), **envios à contabilidade**, **prazos vencidos** e **dados vazados** (o ideal é 0).

### Pegadinhas do servidor que viram regra no código

O servidor reage ao **texto** das mensagens. Por isso, mensagens que disparam ações devem ser **modelos fixos no código**, não texto livre de um modelo de linguagem.

| Código | Pegadinha | O que fazer |
| --- | --- | --- |
| RN-56 | Mensagem para TI, equipamentos ou clínica só aciona quem for citado. Com um id (`ADM-02`) na mensagem, **valem só os ids**; sem id, vale o primeiro ou o último nome | Citar sempre o id, um por mensagem |
| RN-57 | Falar de `contrato` ou `assinar` a um contratado **envia o contrato**; falar de `exame` depois do agendamento **avisa a data** e conta como pedido | Usar essas palavras só nas mensagens que são disso (o revisor bloqueia nas outras) |
| RN-58 | Frases negativas logo antes ("não precisa assinar", "não agendem") não contam, mas qualquer outra menção conta | Evitar negativas e menções de passagem |
| RN-59 | Mensagem que pede um documento (envie, mande, falta, precisamos + o nome do documento) pede esse documento. Citar o nome sem pedir não conta | Pedir com verbo claro |
| RN-60 | Alguns contratados só mandam um documento depois de **pedido**. Se foi pedido antes do primeiro envio, ele chega junto. Se já mandaram um daquele tipo, só mandam outro quando o anterior for **recusado** | Pedir a lista completa já no aceite; **recusar com motivo antes** de pedir o documento novo |
| RN-61 | Responder a um evento com `responder_evento` só conta o texto que o agente escreveu, não o assunto herdado do evento | Escrever o pedido no corpo da resposta |
| RN-62 | Mensagem para endereço que não existe no mundo dá erro 404. Os e-mails vêm das bases `areas` e `contratados` | Nunca digitar e-mail de memória |
| RN-63 | Agradecimentos e conversas sem pedido são entregues e **não têm resposta**. A resposta de `enviar_mensagem` para um contratado não diz se ele vai responder: o time só sabe quando a resposta chega | Não ficar esperando resposta de quem não costuma dar |
| RN-64 | CPF, RG e PIS vêm mascarados com `X` na base (os dados são fictícios). É assim mesmo: usar como estão | Não tentar completar ou corrigir o `X` |
| RN-65 | Falhas: 503 repetir; 504 em ação **conferir antes de repetir** (base `mensagens`, `ler_evento` ou o próprio registro); 409 consultar de novo antes de agir; 410 o cenário acabou; 500 é falha real, avisar a organização | Cliente MCP com timeout de 15 s ou mais |
| RN-66 | Algumas respostas do mundo só chegam "se ainda fizerem sentido" (ex.: a pergunta sobre o exame não chega se o exame já foi feito). Agir rápido muda quais eventos chegam | Tratar como normal, não como erro |

### Decisões em aberto para o time fechar

O servidor não decide estas, e elas mudam o comportamento do agente. Marque quando fechar.

- [ ] **Quem é a pessoa do RH na demo?** Quem digita o nome em `aprovado_por` (precisa ser uma pessoa real do time).
- [ ] **Como a pessoa responde aos pedidos?** Console no terminal, uma página simples ou arquivo.
- [x] **Documento com divergência: aceitar com ressalva ou recusar?** Decidido: é divergência, não recusa. O conferente classifica, o coordenador monta a proposta ao RH, e só com o OK de uma pessoa o agente registra aceito com ressalva e `aprovado_por`. Sem OK o documento fica pendente. Se o RH negar, recusa com motivo e pede comprovante novo. A ficha não exige declaração. No caso da Camila, a mensagem diz só que a conta está no nome do marido e que a casa é do casal, sem certidão de casamento.
- [ ] **Remarcar exame de quem faltou:** o agente remarca sozinho ou propõe ao RH? E quantas vezes no máximo?
- [ ] **Desistência:** que mensagem o agente manda ao contratado e ao gestor, ou só escala?
- [ ] **Contratado sem resposta (o Diego):** além de cobrar no 2º dia e escalar no 4º, o RH pode sugerir adiar a data? Quem avisa o gestor?
- [ ] **Tom das mensagens:** formal ou informal, e se assinam como "Equipe de Admissão".
- [ ] **Acessos específicos do time** (repositório, licença de software, como o pedido da Juliana): o agente só explica que o gestor pede à TI, ou encaminha?
- [ ] **Mensagem de próximos passos** depois do primeiro dia (benefícios, plano de saúde, feedback): o que entra, além do que está na FAQ?

Quando o time marcar estas, o agente passa a ter todas as regras fechadas e os prompts e o código podem citar os códigos RN-xx.
