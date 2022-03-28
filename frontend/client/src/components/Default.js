import React, { Component } from 'react'

export default class Default extends Component {
  render() {
    return (
      <div>
         <video controls>
            <source src="http://192.168.1.149:721/static/v/fall2.mp4" type="video/mp4"></source>
            Your browser does not support the video tag.
          </video> 
      </div>
    )
  }
}
