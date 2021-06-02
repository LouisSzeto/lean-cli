# QUANTCONNECT.COM - Democratizing Finance, Empowering Individuals.
# Lean CLI v1.0. Copyright 2021 QuantConnect Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from datetime import datetime
from typing import Iterator, List, Optional

from lean.models.api import QCFullOrganization, QCResolution
from lean.models.market_hours_database import SecurityType
from lean.models.products.base import Product
from lean.models.products.security import DataType, SecurityProduct


class CryptoProduct(SecurityProduct):
    def __init__(self,
                 data_type: DataType,
                 market: str,
                 ticker: str,
                 resolution: QCResolution,
                 start_date: Optional[datetime],
                 end_date: Optional[datetime]) -> None:
        super().__init__(SecurityType.Crypto, data_type, market, ticker, resolution, start_date, end_date)

    @classmethod
    def get_product_type(cls) -> str:
        return SecurityType.Crypto.value

    @classmethod
    def build(cls, organization: QCFullOrganization) -> List[Product]:
        data_type = cls._ask_data_type([DataType.Trade, DataType.Quote])
        market = cls._ask_market(["Bitfinex", "GDAX"])
        resolution = cls._ask_resolution([QCResolution.Tick,
                                          QCResolution.Second,
                                          QCResolution.Minute,
                                          QCResolution.Hour,
                                          QCResolution.Daily])

        base_directory = f"crypto/{market.lower()}/{resolution.value.lower()}"

        def validate_ticker(t: str) -> bool:
            if resolution == QCResolution.Hour or resolution == QCResolution.Daily:
                return t.lower() in cls._list_files(f"{base_directory}/", fr"/([^/_]+)_{data_type.name.lower()}\.zip")

            return len(cls._list_files(f"{base_directory}/{t.lower()}/", fr"/\d+_{data_type.name.lower()}\.zip")) > 0

        ticker = cls._ask_ticker(SecurityType.Crypto, market, resolution, validate_ticker)

        if resolution != QCResolution.Hour and resolution != QCResolution.Daily:
            dates = cls._list_dates(f"{base_directory}/{ticker.lower()}/", fr"/(\d+)_{data_type.name.lower()}\.zip")
            start_date, end_date = cls._ask_start_end_date(dates)
        else:
            start_date, end_date = None, None

        return [CryptoProduct(data_type, market, ticker, resolution, start_date, end_date)]

    def _get_data_files(self) -> Iterator[str]:
        base_directory = f"crypto/{self._market.lower()}/{self._resolution.value.lower()}"

        if self._resolution == QCResolution.Hour or self._resolution == QCResolution.Daily:
            yield f"{base_directory}/{self._ticker.lower()}_{self._data_type.name.lower()}.zip"
            return

        for date in self._get_dates_with_data():
            yield f"{base_directory}/{self._ticker.lower()}/{date}_{self._data_type.name.lower()}.zip"