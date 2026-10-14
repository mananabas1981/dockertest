import { AppHttp } from "../plugin/app.js";
/* Asynchronous HTTP  */
export const AppHttp2 = async function (url, data = {}, param = null) {
    var req = new Promise(function (resolve, reject) {
        AppHttp(url, data, param, function (o) {
            resolve(o);
        }, function (e) {
            reject(e);
        });
    });

    try {
        return await req;
    } catch (er) {
        console.log(er);
        return null;
    }
};
/* End Asynchronouse */ 