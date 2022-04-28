import React from 'react'

import Video  from '../elements/Video'
import Navbar from '../elements/Navbar'

import "../../css/bootstrap.min.css"
import "../../css/video.css"
import "../../css/WatchPage.css"
import "../../css/global.css"

export default function WatchPage(props)
{
    const { cookies } = props;

    const vprops = {
        //  http://192.168.1.149:721/static/m3u8/RnM_S4E1.m3u8
        //  http://192.168.1.149:721/static/m3u8/fallen_kingdom.m3u8
        m3u8 : "http://192.168.1.149:721/static/m3u8/fallen_kingdom.m3u8",
        autoPlay : false
    };

    const nprops = {
        brand : "~4Nyan~",
        displayUser : cookies.get("username")
    }

    return (
        <div className="apply-font" style={{color: "#fff"}}>
            <Navbar {...nprops}></Navbar>
            <div className="container-fluid">
                <div className="body-container">
                    <div className="row">
                        <div className="col-lg-8 col-md-8 col-sm-fill">

                            <Video {...vprops}></Video>
                            
                            <div className="info-container">
                            
                                <h2 className="title">
                                    <span className="before">[EXPLICIT] </span>
                                    <span className="pretty">Fallen Kingdom Minecraft Perody</span>
                                    <span className="after"> [R18][GONE-WRONG]</span>
                                </h2>

                                <h3 id="gallery_id">
                                    <span className="hash">#</span>398119
                                </h3>
                                
                                <section id="tags">
                                    <div className="tag-container field-name hidden">
                                        Parodies:
                                        <span className="tags"></span>
                                    </div>
                                    
                                    <div className="tag-container field-name hidden">
                                        Characters:
                                        <span className="tags"></span>
                                    </div>
                                    
                                    <div className="tag-container field-name ">
                                        Tags:
                                        <span className="tags">
                                            <a href="/tag/big-breasts/" className="tag tag-2937 ">
                                                <span className="name">big breasts</span>
                                                <span className="count">131K</span>
                                            </a>

                                            <a href="/tag/sole-female/" className="tag tag-35762 ">
                                                <span className="name">sole female</span>
                                                <span className="count">97K</span>
                                            </a>

                                            <a href="/tag/dark-skin/" className="tag tag-19018 ">
                                                <span className="name">dark skin</span>
                                                <span className="count">28K</span>
                                            </a>
                                            
                                            <a href="/tag/x-ray/" className="tag tag-20035 ">
                                                <span className="name">x-ray</span>
                                                <span className="count">26K</span>
                                            </a>

                                            <a href="/tag/sex-toys/" className="tag tag-14971 ">
                                                <span className="name">sex toys</span>
                                                <span className="count">25K</span>
                                            </a>

                                            <a href="/tag/muscle/" className="tag tag-30473 ">
                                                <span className="name">muscle</span>
                                                <span className="count">13K</span>
                                            </a>

                                            <a href="/tag/large-insertions/" className="tag tag-28778 ">
                                                <span className="name">large insertions</span>
                                                <span className="count">1K</span>
                                            </a>

                                        </span>
                                    </div>
                                            
                                    <div className="tag-container field-name ">
                                        Artists:
                                        <span className="tags">
                                            <a href="/artist/sevengar/" className="tag tag-130948 ">
                                                <span className="name">sevengar</span>
                                                <span className="count">31</span>
                                            </a>
                                        </span>
                                    </div>
                                    
                                    <div className="tag-container field-name hidden">
                                        Groups:
                                        <span className="tags"></span>
                                    </div>
                                    
                                    <div className="tag-container field-name ">
                                        Languages:
                                        <span className="tags">
                                            <a href="/language/translated/" className="tag tag-17249 ">
                                                <span className="name">translated</span><span className="count">154K</span>
                                            </a>
                                            
                                            <a href="/language/chinese/" className="tag tag-29963 ">
                                                <span className="name">chinese</span>
                                                <span className="count">69K</span>
                                            </a>  
                                        </span>
                                    </div>
                                    
                                    <div className="tag-container field-name ">
                                        Categories:
                                        <span className="tags">
                                            <a href="/category/doujinshi/" className="tag tag-33172 ">
                                                <span className="name">doujinshi</span>
                                                <span className="count">290K</span>
                                            </a>
                                        </span>
                                    </div>
                                    
                                    <div className="tag-container field-name">
                                        Pages:
                                        <span className="tags"><a className="tag" href="/search/?q=pages%3A%3E7+pages%3A%3C10"><span className="name">9</span>
                                        </a></span>
                                    </div>

                                    <div className="tag-container field-name">
                                        Uploaded:
                                        <span className="tags">
                                            <time className="nobold" dateTime="2022-04-03T17:06:55.992013+00:00" title="4/3/2022, 5:06:55 PM">2 hours, 2 minutes ago</time>
                                        </span>
                                    </div>
                                    
                                </section>
                                
                            </div>
                        
                        </div>

                        <div className="col-lg-4 col-md-2">
                            owo
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
