import http from 'k6/http';

export default function () {
  const url = 'http://polymetrie.orch-team-d.pns-projects.fr.eu.org/track';
  const payload = JSON.stringify({
    "tracker": {
        "WINDOW_LOCATION_HREF": "https://polytech.univ-cotedazur.fr/ecole/association-alumni",
        "WINDOW_LOCATION_ORIGIN": "https://polytech.univ-cotedazur.fr/ecole/association-alumni",
        "USER_AGENT": "Mozilla/5.0",
        "PLATFORM": "Windows 11 Pro x64",
        "TIMEZONE": "UTC+01:00"
    }
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  http.post(url, payload, params);
}
