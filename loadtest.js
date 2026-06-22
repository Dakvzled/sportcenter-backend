import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '10s', target: 20 }, // +20 user bersamaan dalam 10 detik
    { duration: '30s', target: 20 }, // Tahan 20 user konstan selama 30 detik
    { duration: '10s', target: 0 },  // Turunkan pelan-pelan ke 0 user
  ],
  thresholds: {
    // Toleransi kegagalan: 95% dari request harus selesai di bawah 500ms
    http_req_duration: ['p(95)<500'],
    // Toleransi error: Kegagalan request tidak boleh lebih dari 1%
    http_req_failed: ['rate<0.01'],
  },
};

const BASE_URL = 'http://127.0.0.1:8000/api';

export default function () {
  // 1. Skenario Login
  const loginPayload = JSON.stringify({
    email: 'wargasolo@gmail.com', // Ganti dengan email valid di DB Anda
    password: 'wargasolobiasa'    // Ganti dengan password valid
  });

  const params = {
    headers: { 'Content-Type': 'application/json' },
  };

  const loginRes = http.post(`${BASE_URL}/login/`, loginPayload, params);

  // Validasi Login
  const isLoginSuccessful = check(loginRes, {
    'Status login 200': (r) => r.status === 200,
    'Mendapat token akses': (r) => r.json('access') !== undefined,
  });

  // Hentikan iterasi virtual user jika login gagal (mencegah error berantai)
  if (!isLoginSuccessful) {
    sleep(1);
    return;
  }

  const token = loginRes.json('access');
  
  const authParams = {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  };

  // 2. Skenario Menarik Data Daftar Lapangan
  const fieldsRes = http.get(`${BASE_URL}/fields/`, authParams);
  check(fieldsRes, {
    'Berhasil tarik data lapangan (status 200)': (r) => r.status === 200,
  });

  sleep(1); 

  const today = new Date().toISOString().split('T')[0]; // Format YYYY-MM-DD
  const bookingsRes = http.get(`${BASE_URL}/bookings/?field=1&date=${today}`, authParams);
  
  check(bookingsRes, {
    'Berhasil tarik jadwal (status 200)': (r) => r.status === 200,
  });


  sleep(1);
}