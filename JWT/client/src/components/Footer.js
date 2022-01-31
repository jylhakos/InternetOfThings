import React from 'react'

const Footer = () => {
 
  const footerStyle = {
    color: 'green',
    paddingTop: '50px',
    fontStyle: 'italic',
    fontSize: 16
  }

  return (
    <div style={footerStyle}>
      <br />
      <em>Powered by Node.js</em>
    </div>
  )
}

export default Footer