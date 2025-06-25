import { useEffect, useState } from 'react';

function Logo() {
  const [logoUrl, setLogoUrl] = useState('');

  useEffect(() => {
    fetch('/logo-url')
      .then(res => res.json())
      .then(data => setLogoUrl(data.url));
  }, []);

  if (!logoUrl) return null;
  return <img src={logoUrl} alt="Logo" />;
}

export default Logo;