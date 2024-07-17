import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QGridLayout, QTableWidget, QTableWidgetItem

class CalculatorApp(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('SSB Calculator Basic')
        self.resize(1000, 900)  # 設定窗口大小，寬1000，高900

        layout = QVBoxLayout()
        
        author_info = QLabel('Author: Dustin_Chen, Email: Dustin_Chen@compal.com or chuhpsdustin@gmail.com')
        layout.addWidget(author_info)
        
        examples_info = QLabel('Please input (band, carrierBw(RB), freq_low, freq_high), then it will calculate gscn, PointA, Ssb, CenterFreq, Kssb, offsetToPointA\n'
                               'n41 => freq range [2496000, 2690000], arfcn range [499200, 538000]\n'
                               'n48 => freq range [3550000, 3700000], arfcn range [636667, 646667]\n'
                               'n78 => freq range [3300000, 3800000], arfcn range [620000, 653333]\n'
                               'n79 => freq range [4400000, 5000000], arfcn range [693333, 733333]\n'
                               'ex:(band, carrierBw(RB), freq_low, freq_high) = (78, 273, 3603840, 3603840) / (79, 273, 4849860,4849860) / (41, 273, 2565750, 2565750)')
        layout.addWidget(examples_info)
        
        grid = QGridLayout()

        grid.addWidget(QLabel('Band:'), 0, 0)
        self.band_input = QLineEdit('78')
        grid.addWidget(self.band_input, 0, 1)

        grid.addWidget(QLabel('Carrier Bandwidth (RB):'), 1, 0)
        self.carrier_bw_input = QLineEdit('273')
        grid.addWidget(self.carrier_bw_input, 1, 1)

        grid.addWidget(QLabel('Frequency Low (kHz):'), 2, 0)
        self.freq_low_input = QLineEdit('3603840')
        grid.addWidget(self.freq_low_input, 2, 1)

        grid.addWidget(QLabel('Frequency High (kHz):'), 3, 0)
        self.freq_high_input = QLineEdit('3603840')
        grid.addWidget(self.freq_high_input, 3, 1)

        self.calc_button = QPushButton('Calculate')
        self.calc_button.clicked.connect(self.calculate)
        grid.addWidget(self.calc_button, 4, 0, 1, 2)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addLayout(grid)
        layout.addWidget(self.result_text)

        self.setLayout(layout)
    
    def calculate(self):
        band = int(self.band_input.text())
        carrier_bw = int(self.carrier_bw_input.text())
        freq_low = int(self.freq_low_input.text())
        freq_high = int(self.freq_high_input.text())

        result = self.calculate_values(band, carrier_bw, freq_low, freq_high)
        self.result_text.setText(result)
    
    def calculate_values(self, band, carrier_bw, freq_low, freq_high):
        subCarrierSpacing = 30
        offsetToCarrier = 0

        nrBand = [
            {'band': 41, 'lowest_freq': 2496000, 'highest_freq': 2690000, 'lowest_n_ref': 499200, 'highest_n_ref': 537996, 'n_ref_step': 6, 'lowest_gscn': 6252, 'highest_gscn': 6714, 'gscn_step': 3},
            {'band': 48, 'lowest_freq': 3550000, 'highest_freq': 3700000, 'lowest_n_ref': 636668, 'highest_n_ref': 646666, 'n_ref_step': 2, 'lowest_gscn': 7884, 'highest_gscn': 7982, 'gscn_step': 1},
            {'band': 78, 'lowest_freq': 3300000, 'highest_freq': 3800000, 'lowest_n_ref': 620000, 'highest_n_ref': 653332, 'n_ref_step': 2, 'lowest_gscn': 7711, 'highest_gscn': 8051, 'gscn_step': 1},
            {'band': 79, 'lowest_freq': 4400000, 'highest_freq': 5000000, 'lowest_n_ref': 693334, 'highest_n_ref': 733332, 'n_ref_step': 2, 'lowest_gscn': 8480, 'highest_gscn': 8880, 'gscn_step': 16},
            {'band': 79, 'lowest_freq': 4400000, 'highest_freq': 5000000, 'lowest_n_ref': 693334, 'highest_n_ref': 733332, 'n_ref_step': 2, 'lowest_gscn': 8475, 'highest_gscn': 8884, 'gscn_step': 1}
        ]

        def lowFreqCalc(nrBandIndex, coreset0RB, coreset0offset):
            result = ""
            if nrBand[nrBandIndex]['gscn_step'] == 1:
                for N in range(1, 2500):
                    for M in range(1, 6, 2):
                        gscn = 3 * N + (M - 3) / 2
                        if nrBand[nrBandIndex]['lowest_gscn'] <= gscn <= nrBand[nrBandIndex]['highest_gscn']:
                            for n_ref in range(nrBand[nrBandIndex]['lowest_n_ref'], nrBand[nrBandIndex]['highest_n_ref'] + 1, nrBand[nrBandIndex]['n_ref_step']):
                                if 5 * n_ref == N * 1200 + M * 50:
                                    absFreqSsb = N * 1200 + M * 50
                                    for freq in range(nrBand[nrBandIndex]['lowest_n_ref'] * 5, nrBand[nrBandIndex]['highest_n_ref'] * 5 + 1, nrBand[nrBandIndex]['n_ref_step'] * 15):
                                        if freq_low <= freq <= freq_high:
                                            nDlCenterFreq = freq
                                            dlEarfcn = nDlCenterFreq / 5
                                            absFreqPointA = nDlCenterFreq - carrier_bw * 12 * subCarrierSpacing / 2 - offsetToCarrier * 12 * subCarrierSpacing
                                            absArfcnPointA = absFreqPointA / 5
                                            Kssb = (absFreqSsb - 10 * 12 * subCarrierSpacing - absFreqPointA) % (subCarrierSpacing * 12) / 15
                                            offsetToPointA = (absFreqSsb - 10 * 12 * subCarrierSpacing - Kssb * 15 - absFreqPointA) / (15 * 12)
                                            if (nDlCenterFreq + carrier_bw * 12 * subCarrierSpacing / 2 >= absFreqSsb - 10 * 12 * subCarrierSpacing - Kssb * 15 - coreset0offset * 12 * subCarrierSpacing + coreset0RB * 12 * subCarrierSpacing) and (nDlCenterFreq - carrier_bw * 12 * subCarrierSpacing / 2 <= absFreqSsb - 10 * 12 * subCarrierSpacing - Kssb * 15 - coreset0offset * 12 * subCarrierSpacing):
                                                if Kssb >= 0:
                                                    result += f"gscn={gscn}, absFreqPointA={absFreqPointA}, absArfcnPointA={absArfcnPointA}, absFreqSsb={absFreqSsb}, absArfcnSsb={n_ref}, dlEarfcn={dlEarfcn}, nDlCenterFreq={nDlCenterFreq}, Kssb={Kssb}, offsetToPointA={offsetToPointA}\n"
            return result

        def midFreqCalc(nrBandIndex, coreset0RB, coreset0offset):
            result = ""
            for gscn in range(nrBand[nrBandIndex]['lowest_gscn'], nrBand[nrBandIndex]['highest_gscn'] + 1, nrBand[nrBandIndex]['gscn_step']):
                for n_ref in range(nrBand[nrBandIndex]['lowest_n_ref'], nrBand[nrBandIndex]['highest_n_ref'] + 1, nrBand[nrBandIndex]['n_ref_step']):
                    if (gscn - 7499) * 96 == (n_ref - 600000):
                        absFreqSsb = 3000000 + (gscn - 7499) * 1440
                        for freq in range((nrBand[nrBandIndex]['lowest_n_ref'] - 600000) * 15 + 3000000, (nrBand[nrBandIndex]['highest_n_ref'] - 600000) * 15 + 3000000 + 1, nrBand[nrBandIndex]['n_ref_step'] * 15):
                            if freq_low <= freq <= freq_high:
                                nDlCenterFreq = freq
                                dlEarfcn = (nDlCenterFreq - 3000000) / 15 + 600000
                                absFreqPointA = nDlCenterFreq - carrier_bw * 12 * subCarrierSpacing / 2 - offsetToCarrier * 12 * subCarrierSpacing
                                absArfcnPointA = (absFreqPointA - 3000000) / 15 + 600000
                                Kssb = (absFreqSsb - 10 * 12 * subCarrierSpacing - absFreqPointA) % (subCarrierSpacing * 12) / 15
                                offsetToPointA = (absFreqSsb - 10 * 12 * subCarrierSpacing - Kssb * 15 - absFreqPointA) / (15 * 12)
                                if (nDlCenterFreq + carrier_bw * 12 * subCarrierSpacing / 2 >= absFreqSsb - 10 * 12 * subCarrierSpacing - Kssb * 15 - coreset0offset * 12 * subCarrierSpacing + coreset0RB * 12 * subCarrierSpacing) and (nDlCenterFreq - carrier_bw * 12 * subCarrierSpacing / 2 <= absFreqSsb - 10 * 12 * subCarrierSpacing - Kssb * 15 - coreset0offset * 12 * subCarrierSpacing):
                                    if Kssb >= 0:
                                        result += f"gscn={gscn}, absFreqPointA={absFreqPointA}, absArfcnPointA={absArfcnPointA}, absFreqSsb={absFreqSsb}, absArfcnSsb={n_ref}, dlEarfcn={dlEarfcn}, nDlCenterFreq={nDlCenterFreq}, Kssb={Kssb}, offsetToPointA={offsetToPointA}\n"
            return result

        def highFreqCalc(nrBandIndex, coreset0RB, coreset0offset):
            result = ""
            for gscn in range(nrBand[nrBandIndex]['lowest_gscn'], nrBand[nrBandIndex]['highest_gscn'] + 1, nrBand[nrBandIndex]['gscn_step']):
                for n_ref in range(nrBand[nrBandIndex]['lowest_n_ref'], nrBand[nrBandIndex]['highest_n_ref'] + 1, nrBand[nrBandIndex]['n_ref_step']):
                    if (gscn - 22255) * 72 == (n_ref - 2016667):
                        absFreqSsb = 6420000 + (gscn - 22255) * 720
                        for freq in range((nrBand[nrBandIndex]['lowest_n_ref'] - 2016667) * 15 + 6420000, (nrBand[nrBandIndex]['highest_n_ref'] - 2016667) * 15 + 6420000 + 1, nrBand[nrBandIndex]['n_ref_step'] * 15):
                            if freq_low <= freq <= freq_high:
                                nDlCenterFreq = freq
                                dlEarfcn = (nDlCenterFreq - 6420000) / 15 + 2016667
                                absFreqPointA = nDlCenterFreq - carrier_bw * 12 * subCarrierSpacing / 2 - offsetToCarrier * 12 * subCarrierSpacing
                                absArfcnPointA = (absFreqPointA - 6420000) / 15 + 2016667
                                Kssb = (absFreqSsb - 10 * 12 * subCarrierSpacing - absFreqPointA) % (subCarrierSpacing * 12) / 15
                                offsetToPointA = (absFreqSsb - 10 * 12 * subCarrierSpacing - Kssb * 15 - absFreqPointA) / (15 * 12)
                                if (nDlCenterFreq + carrier_bw * 12 * subCarrierSpacing / 2 >= absFreqSsb - 10 * 12 * subCarrierSpacing - Kssb * 15 - coreset0offset * 12 * subCarrierSpacing + coreset0RB * 12 * subCarrierSpacing) and (nDlCenterFreq - carrier_bw * 12 * subCarrierSpacing / 2 <= absFreqSsb - 10 * 12 * subCarrierSpacing - Kssb * 15 - coreset0offset * 12 * subCarrierSpacing):
                                    if Kssb >= 0:
                                        result += f"gscn={gscn}, absFreqPointA={absFreqPointA}, absArfcnPointA={absArfcnPointA}, absFreqSsb={absFreqSsb}, absArfcnSsb={n_ref}, dlEarfcn={dlEarfcn}, nDlCenterFreq={nDlCenterFreq}, Kssb={Kssb}, offsetToPointA={offsetToPointA}\n"
            return result

        for i in range(len(nrBand)):
            if band == nrBand[i]['band']:
                result = ""
                if band == 41:
                    result = lowFreqCalc(i, 24, 0)
                elif band == 48 or band == 78:
                    result = midFreqCalc(i, 24, 0)
                elif band == 79:
                    result = highFreqCalc(i, 24, 0)
                return result
        
        return "Invalid band input"

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = CalculatorApp()
    ex.show()
    sys.exit(app.exec_())
