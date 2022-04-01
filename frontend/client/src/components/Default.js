import React, { Component } from 'react'
import Video from './Video'

export default class Default extends Component 
{
  render() 
  {

    let props = {
      m3u8 : "http://192.168.1.149:721/static/m3u8/fallen_kingdom.m3u8",
    };

    return (
      <div>
        <Video {...props}></Video>
      </div>
    )
  }
}
