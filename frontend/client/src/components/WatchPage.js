import React, { Component } from 'react'
import Video from './Video'
import Navbar from './Navbar'

import "../css/bootstrap.min.css"
import "../css/video.css"
import "../css/WatchPage.css"

export default class WatchPage extends Component 
{
  render() 
  {

    let vprops = {
      //  http://192.168.1.149:721/static/m3u8/RnM_S4E1.m3u8
      //  http://192.168.1.149:721/static/m3u8/fallen_kingdom.m3u8
      m3u8 : "http://192.168.1.149:721/static/m3u8/RnM_S4E1.m3u8",
      autoPlay : false
    };

    let nprops = {
        brand : "~4Nyan~"
    }

    return (
        <div>
            <Navbar {...nprops}></Navbar>
            <div class="container-fluid">
                <div class="body-container">
                    <div class="row">
                        <div class="col-lg-8 col-md-8 col-sm-fill">
                            <Video {...vprops}>hello world</Video>
                        </div>

                        <div class="col-lg-4 col-md-2">
                            owo
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
  }
}
