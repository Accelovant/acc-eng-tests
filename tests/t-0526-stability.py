from datetime import timedelta, datetime
from time import sleep
from acc_py_inst import MpxInst, DaeRo16, Keysight34461a

class T0526Stability():
    def __init__(self):
        self.cycles = 5
        self.duration = timedelta(minutes=15)
        self.sample_period = timedelta(seconds=2)
        self.temperature_setpoint = 50
        self.default_averaging = 1
        self.channels = 5
        self.samples = int(self.duration / self.sample_period)

        self.mpx = MpxInst(port='COM1', use_modbus=True)
        self.dmm = Keysight34461a()
        self.dmm.parse_config(func_type='CURR:DC',
                              sense_range=0.1,
                              int_time=0.2)
        self.dmm_samples = 8
        self.metrics = []

    def _set_temperature(self, temp):
        pass

    def _read_temp_from_channel(self, chan):
        chan_group = [1]*chan + [0]*(self.channels - chan)
        DaeRo16.set_relay_group(chan_group)
        res = {'mpx_modbus_temperature_in_C': self.mpx.get_temperature(chan)}
        res['i420_current_in_A'] = self.dmm.get_avg_dc_a(self.dmm_samples)
        return res


    def run(self):
        self.metrics = []
        self._set_temperature(self.temperature_setpoint)
        for cycle in range(self.cycles):
            for sample in self.samples:
                t = datetime.now()
                for chan in range(self.channels):
                    res = self._read_temp_from_channel(chan)
                    res['cycle'] = cycle
                    res['channel'] = chan
                    res['timestamp'] = datetime.now().isoformat()
                    res['sample'] = sample
                    self.metrics.append(res)
                offset = datetime.now() - t
                sleep((self.sample_period - offset).total_seconds())
        return self.metrics

t = T0526Stability()
print(vars(t))