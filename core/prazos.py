"""
Dias úteis e varredura de prazos.

Responsabilidades:
- Calcular dias úteis (seg-sex, 08:00-18:00)
- Varrer prazos de resposta das áreas (TI, Equipamentos, Clínica: 2 dias úteis)
- Disparar cobranças quando prazo vence
- Usar campo `agora` da resposta do servidor como relógio oficial
- Relógio simulado: 1 hora simulada = 12 s reais

Prazos:
- TI: 2 dias úteis
- Equipamentos: 2 dias úteis
- Clínica: agenda às 09:00, 2 dias úteis depois do pedido
- Contrato: 1 dia útil
- Exame: 1 dia útil
- Documento: 3 dias úteis
"""

import logging
from datetime import datetime, timedelta
from typing import List, Tuple

# TODO: implementar verificação de dia útil
# TODO: implementar cálculo de próximo dia útil
# TODO: implementar cálculo de dias úteis entre duas datas
# TODO: implementar varredura de prazos
# TODO: implementar disparo de cobranças
# TODO: implementar sincronização com relógio do servidor
