import React from 'react'
import Nav from "../elements/Navbar";
import "../../css/video.css"


export default function Default(props)
{
    const { cookies } = props;

    let vprops = {
        m3u8 : "http://192.168.1.149:721/static/m3u8/RnM_S4E1.m3u8",
        autoPlay : false
    };

    let nprops = {
        brand : "~4Nyan~",
        displayUser : cookies.get("username")
    };

    console.log(cookies.get("user"));

    return (
      <div>
        <div>
          <Nav {...nprops}></Nav>
          {/* <Video {...props}></Video> */}
        </div>
      </div>
    )
}
