import { Mail, Phone, MapPin, Clock } from 'lucide-react';

export default function Footer() {
  return (
    <footer style={{
      background: 'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)',
      borderTop: '2px solid #dc2626',
      marginTop: '4rem',
      padding: '3rem 2rem 1.5rem',
      color: '#94a3b8'
    }}>
      <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
          gap: '2rem',
          marginBottom: '2rem'
        }}>
          {/* Company Info */}
          <div>
            <h3 style={{ color: '#fff', fontSize: '1.25rem', marginBottom: '1rem', fontWeight: '700' }}>
              Hero MotoCorp
            </h3>
            <p style={{ fontSize: '0.875rem', lineHeight: '1.6', marginBottom: '1rem' }}>
              India's largest two-wheeler manufacturer providing world-class service and maintenance solutions
              through AI-powered predictive technology.
            </p>
            <div style={{ 
              background: 'linear-gradient(135deg, #991b1b 0%, #dc2626 100%)',
              padding: '0.5rem 1rem',
              borderRadius: '0.5rem',
              display: 'inline-block',
              fontSize: '0.75rem',
              fontWeight: '600',
              color: '#fff',
              letterSpacing: '0.05em'
            }}>
              AUTHORIZED SERVICE CENTER
            </div>
          </div>

          {/* Contact Info */}
          <div>
            <h3 style={{ color: '#fff', fontSize: '1.1rem', marginBottom: '1rem', fontWeight: '600' }}>
              Contact Information
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.875rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Phone size={16} style={{ color: '#dc2626' }} />
                <span>1800-266-0018 (Toll Free)</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Mail size={16} style={{ color: '#dc2626' }} />
                <span>service@heromotocorp.com</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'start', gap: '0.5rem' }}>
                <MapPin size={16} style={{ color: '#dc2626', marginTop: '0.15rem' }} />
                <span>The Grand Plaza, Plot No. 2,<br/>Nelson Mandela Road, Vasant Kunj,<br/>New Delhi - 110070</span>
              </div>
            </div>
          </div>

          {/* Service Hours */}
          <div>
            <h3 style={{ color: '#fff', fontSize: '1.1rem', marginBottom: '1rem', fontWeight: '600' }}>
              Service Hours
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.875rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Clock size={16} style={{ color: '#dc2626' }} />
                <div>
                  <div style={{ fontWeight: '600', color: '#fff' }}>Monday - Saturday</div>
                  <div>9:00 AM - 7:00 PM</div>
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Clock size={16} style={{ color: '#dc2626' }} />
                <div>
                  <div style={{ fontWeight: '600', color: '#fff' }}>Sunday</div>
                  <div>10:00 AM - 5:00 PM</div>
                </div>
              </div>
              <div style={{
                background: 'rgba(34, 197, 94, 0.2)',
                padding: '0.5rem',
                borderRadius: '0.375rem',
                border: '1px solid rgba(34, 197, 94, 0.3)',
                marginTop: '0.5rem'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <span style={{ 
                    width: '8px', 
                    height: '8px', 
                    background: '#22c55e', 
                    borderRadius: '50%',
                    display: 'inline-block',
                    animation: 'pulse 2s infinite'
                  }}></span>
                  <span style={{ color: '#86efac', fontWeight: '600', fontSize: '0.8rem' }}>
                    Emergency Service Available 24/7
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h3 style={{ color: '#fff', fontSize: '1.1rem', marginBottom: '1rem', fontWeight: '600' }}>
              Quick Links
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.875rem' }}>
              <a href="#" style={{ color: '#94a3b8', textDecoration: 'none', transition: 'color 0.2s' }}
                 onMouseOver={(e) => e.target.style.color = '#dc2626'}
                 onMouseOut={(e) => e.target.style.color = '#94a3b8'}>
                → Book Service Appointment
              </a>
              <a href="#" style={{ color: '#94a3b8', textDecoration: 'none', transition: 'color 0.2s' }}
                 onMouseOver={(e) => e.target.style.color = '#dc2626'}
                 onMouseOut={(e) => e.target.style.color = '#94a3b8'}>
                → Track Vehicle Health
              </a>
              <a href="#" style={{ color: '#94a3b8', textDecoration: 'none', transition: 'color 0.2s' }}
                 onMouseOver={(e) => e.target.style.color = '#dc2626'}
                 onMouseOut={(e) => e.target.style.color = '#94a3b8'}>
                → Service History
              </a>
              <a href="#" style={{ color: '#94a3b8', textDecoration: 'none', transition: 'color 0.2s' }}
                 onMouseOver={(e) => e.target.style.color = '#dc2626'}
                 onMouseOut={(e) => e.target.style.color = '#94a3b8'}>
                → Warranty Information
              </a>
              <a href="#" style={{ color: '#94a3b8', textDecoration: 'none', transition: 'color 0.2s' }}
                 onMouseOver={(e) => e.target.style.color = '#dc2626'}
                 onMouseOut={(e) => e.target.style.color = '#94a3b8'}>
                → Spare Parts Catalog
              </a>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div style={{ 
          borderTop: '1px solid #334155', 
          paddingTop: '1.5rem', 
          marginTop: '2rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '1rem',
          fontSize: '0.875rem'
        }}>
          <div>
            © 2025 Hero MotoCorp Ltd. All rights reserved.
          </div>
          <div style={{ display: 'flex', gap: '1.5rem' }}>
            <a href="#" style={{ color: '#94a3b8', textDecoration: 'none', transition: 'color 0.2s' }}
               onMouseOver={(e) => e.target.style.color = '#dc2626'}
               onMouseOut={(e) => e.target.style.color = '#94a3b8'}>
              Privacy Policy
            </a>
            <a href="#" style={{ color: '#94a3b8', textDecoration: 'none', transition: 'color 0.2s' }}
               onMouseOver={(e) => e.target.style.color = '#dc2626'}
               onMouseOut={(e) => e.target.style.color = '#94a3b8'}>
              Terms of Service
            </a>
            <a href="#" style={{ color: '#94a3b8', textDecoration: 'none', transition: 'color 0.2s' }}
               onMouseOver={(e) => e.target.style.color = '#dc2626'}
               onMouseOut={(e) => e.target.style.color = '#94a3b8'}>
              Support
            </a>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      `}</style>
    </footer>
  );
}
