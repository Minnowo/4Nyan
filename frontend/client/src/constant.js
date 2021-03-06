
const API_ENDPOINTS = {
    // backend_ref : "http://192.168.1.149:721/",
    backend_ref : "http://localhost:721/",
    login : "auth/token/",
    register : "create/user/",
    upload_file : "create/file/",
    create_tag : "create/tag",
    static : {
        video : "static/v/",
        image : "static/i/",
        m38u  : "static/m3u8/",
    },
    search : {
        get_files : "search/get_files",
        get_file_tags : "search/get_file_tags",
    }
};

export const ROUTES = {
        default  : "/",
        home     : "/home",
        watch    : "/watch",
        images   : "/images",
        image    : "/image",
        login    : "/login",
        register : "/register",
        upload   : "/upload",
}

export const MAX_PASSWORD_LENGTH = 96;
export const MIN_PASSWORD_LENGTH = 1;

export const MAX_USERNAME_LENGTH = 32;
export const MIN_USERNAME_LENGTH = 4;

export default API_ENDPOINTS;