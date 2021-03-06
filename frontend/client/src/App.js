import React from 'react';
import {BrowserRouter as Router,Routes,Route} from "react-router-dom";
import Cookies from 'universal-cookie';

import { ROUTES } from './constant';

import Default from './components/pages/Default';
import WatchPage from './components/pages/WatchPage';
import LoginPage from './components/pages/LoginPage';
import RegisterPage from './components/pages/SignupPage';
import UploadPage from './components/pages/UploadPage';
import CreateTag from './components/tests/CreateTag';
import ImagesPage from './components/pages/ImagesPage';
import ImagePage from './components/pages/ImagePage';


export default function App()
{
    const [state, setState] = React.useState({ 
      cookies : new Cookies()
    });
    
    return (
      <Router>
        <Routes>
        <Route path={ROUTES.default} element={<Default {...state} />}></Route>
        <Route path={ROUTES.home} element={<Default {...state}/>}></Route>
        <Route path={ROUTES.watch} element={<WatchPage {...state}/>}></Route>
        <Route path={ROUTES.images} element={<ImagesPage {...state}/>}></Route>
        <Route path={ROUTES.image + "/:id"} element={<ImagePage {...state}/>}></Route>
        <Route path={ROUTES.login} element={<LoginPage {...state}/>}></Route>
        <Route path={ROUTES.register} element={<RegisterPage {...state}/>}></Route>
        <Route path={ROUTES.upload} element={<UploadPage {...state}/>}></Route>
        <Route path={"/test"} element={<CreateTag {...state}/>}></Route>
        </Routes>
      </Router>
    );
}
