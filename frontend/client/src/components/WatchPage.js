import React, { Component } from 'react'
import Video from './Video'
import Navbar from './Navbar'

import "../css/bootstrap.min.css"
import "../css/video.css"
import "../css/WatchPage.css"
import "../css/global.css"

export default class WatchPage extends Component 
{
  render() 
  {

    let vprops = {
      //  http://192.168.1.149:721/static/m3u8/RnM_S4E1.m3u8
      //  http://192.168.1.149:721/static/m3u8/fallen_kingdom.m3u8
      m3u8 : "http://192.168.1.149:721/static/m3u8/fallen_kingdom.m3u8",
      autoPlay : false
    };

    let nprops = {
        brand : "~4Nyan~"
    }

    return (
        <div class="apply-font" style={{color: "#fff"}}>
            <Navbar {...nprops}></Navbar>
            <div class="container-fluid">
                <div class="body-container">
                    <div class="row">
                        <div class="col-lg-8 col-md-8 col-sm-fill">

                            <Video {...vprops}></Video>
                            
                            <div class="info-container">
                               
                                <h2 class="title">
                                    <span class="before">[EXPLICIT] </span>
                                    <span class="pretty">Fallen Kingdom Minecraft Perody</span>
                                    <span class="after"> [R18][GONE-WRONG]</span>
                                </h2>

                                <h3 id="gallery_id">
                                    <span class="hash">#</span>398119
                                </h3>
                                
                                <section id="tags">
                                    <div class="tag-container field-name hidden">
								        Parodies:
								        <span class="tags"></span>
                                    </div>
                                    
                                    <div class="tag-container field-name hidden">
								        Characters:
								        <span class="tags"></span>
                                    </div>
                                    
                                    <div class="tag-container field-name ">
								        Tags:
								        <span class="tags">
                                            <a href="/tag/big-breasts/" class="tag tag-2937 ">
                                                <span class="name">big breasts</span>
                                                <span class="count">131K</span>
                                            </a>

                                            <a href="/tag/sole-female/" class="tag tag-35762 ">
                                                <span class="name">sole female</span>
                                                <span class="count">97K</span>
                                            </a>

                                            <a href="/tag/dark-skin/" class="tag tag-19018 ">
                                                <span class="name">dark skin</span>
                                                <span class="count">28K</span>
                                            </a>
                                            
                                            <a href="/tag/x-ray/" class="tag tag-20035 ">
                                                <span class="name">x-ray</span>
                                                <span class="count">26K</span>
                                            </a>

                                            <a href="/tag/sex-toys/" class="tag tag-14971 ">
                                                <span class="name">sex toys</span>
                                                <span class="count">25K</span>
                                            </a>

                                            <a href="/tag/muscle/" class="tag tag-30473 ">
                                                <span class="name">muscle</span>
                                                <span class="count">13K</span>
                                            </a>

                                            <a href="/tag/large-insertions/" class="tag tag-28778 ">
                                                <span class="name">large insertions</span>
                                                <span class="count">1K</span>
                                            </a>

                                        </span>
                                    </div>
                                            
                                    <div class="tag-container field-name ">
                                        Artists:
                                        <span class="tags">
                                            <a href="/artist/sevengar/" class="tag tag-130948 ">
                                                <span class="name">sevengar</span>
                                                <span class="count">31</span>
                                            </a>
                                        </span>
                                    </div>
                                    
                                    <div class="tag-container field-name hidden">
                                        Groups:
                                        <span class="tags"></span>
                                    </div>
                                    
                                    <div class="tag-container field-name ">
                                        Languages:
                                        <span class="tags">
                                            <a href="/language/translated/" class="tag tag-17249 ">
                                                <span class="name">translated</span><span class="count">154K</span>
                                            </a>
                                            
                                            <a href="/language/chinese/" class="tag tag-29963 ">
                                                <span class="name">chinese</span>
                                                <span class="count">69K</span>
                                            </a>  
                                        </span>
                                    </div>
                                    
                                    <div class="tag-container field-name ">
                                        Categories:
                                        <span class="tags">
                                            <a href="/category/doujinshi/" class="tag tag-33172 ">
                                                <span class="name">doujinshi</span>
                                                <span class="count">290K</span>
                                            </a>
                                        </span>
                                    </div>
                                    
                                    <div class="tag-container field-name">
                                        Pages:
                                        <span class="tags"><a class="tag" href="/search/?q=pages%3A%3E7+pages%3A%3C10"><span class="name">9</span>
                                        </a></span>
                                    </div>

                                    <div class="tag-container field-name">
                                        Uploaded:
                                        <span class="tags">
                                            <time class="nobold" datetime="2022-04-03T17:06:55.992013+00:00" title="4/3/2022, 5:06:55 PM">2 hours, 2 minutes ago</time>
                                        </span>
                                    </div>
                                    
                                </section>
                                 
                            </div>
                        
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
