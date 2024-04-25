using UnityEngine;
using System.Collections;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Net.Sockets;
using System.Net;
using System.IO;
using System.Threading;
using System.Diagnostics;
using System.Reflection;
using System.Text.RegularExpressions;

public class HTTPServer : MonoBehaviour
{
    [SerializeField] int mPort = 12366;
    [SerializeField] int bufferSize = 16;

    public bool OnLive { private set; get; }

    public void StartLive()
    {
        UnityEngine.Debug.Log("HTTP StartLive");
        OnLive = true;
        StartServer();
    }

    public void StopLive()
    {
        OnLive = false;
        //Kill_All_Python_Process();
        StopServer();
    }

    void Start()
    {
        DontDestroyOnLoad(gameObject);
        StartServer();
    }

    void OnDestroy()
    {
        StopServer();
    }

    private Thread mServerThread;
    private HttpListener mListener;
    List<string> mRecvMessages = new List<string>();

    public List<string> GetRecvMessages()
    {
        return mRecvMessages;
    }

    List<string> _GetRecvMessages(string strInput)
    {
        List<string> msgs = new List<string>();
        Regex reg = new Regex("\\[[^&.]+");
        var ms = reg.Matches(strInput);
        foreach (Match match in ms)
        {
            msgs.Add(match.Value);
        }
        return msgs;
    }

    public void StartServer()
    {
        StopServer();
        string url = "http://127.0.0.1:" + mPort + "/";
        UnityEngine.Debug.Log(url);
        Initialize();
    }

    public void StopServer()
    {
        if (mServerThread != null)
            mServerThread.Abort();
        if (mListener != null)
            mListener.Stop();
    }

    private void Listen()
    {
        mListener = new HttpListener();
        mListener.Prefixes.Add("http://*:" + mPort.ToString() + "/");
        mListener.Start();
        while (true)
        {
            try
            {
                HttpListenerContext context = mListener.GetContext();
                Process(context);
            }
            catch (Exception ex)
            {
                UnityEngine.Debug.Log(ex);
            }
        }
    }

    private void Process(HttpListenerContext context)
    {
        string methodName = context.Request.Url.Segments[1].Replace("/", "");
        //if (methodName != null)
        {
            context.Response.ContentType = "application/json";

            object result = null;
            try
            {
                string dest_string = "";
                using (Stream st = context.Request.InputStream)
                {
                    StreamReader sr = new StreamReader(st, Encoding.UTF8);
                    dest_string = sr.ReadToEnd();
                }
                dest_string = dest_string.Replace("msgs=", "");
                dest_string = WWW.UnEscapeURL(dest_string);
                mRecvMessages = _GetRecvMessages(dest_string);
                //UnityEngine.Debug.Log(dest_string);
                foreach (var item in mRecvMessages)
                {
                    UnityEngine.Debug.Log(item);
                }
                //UnityEngine.Debug.Log(mRecvMessages.Count);
                //UnityEngine.Debug.Log(mRecvMessages[0]);

                // 一定要回复，不然后续不对
                string jsonString = "ok";
                //jsonString = JsonUtility.ToJson(result);
                byte[] jsonByte = Encoding.UTF8.GetBytes(jsonString);
                context.Response.ContentLength64 = jsonByte.Length;
                Stream jsonStream = new MemoryStream(jsonByte);
                byte[] buffer = new byte[1024 * bufferSize];
                int nbytes;
                while ((nbytes = jsonStream.Read(buffer, 0, buffer.Length)) > 0)
                    context.Response.OutputStream.Write(buffer, 0, nbytes);
                jsonStream.Close();
            }
            catch (Exception ex)
            {
                context.Response.StatusCode = (int)HttpStatusCode.InternalServerError;
                UnityEngine.Debug.LogError(ex);
                context.Response.StatusDescription = ex.Message;
                context.Response.OutputStream.Flush();
                context.Response.OutputStream.Close();
            }
        }
    }

    private void Initialize()
    {
        mServerThread = new Thread(this.Listen);
        mServerThread.Start();
    }

    //bool mOnLive = false;
    //void OnGUI()
    //{
    //    if (GUILayout.Button(mOnLive ? "停止监听" : "开始监听"))
    //    {
    //        mOnLive = !mOnLive;
    //        if (mOnLive)
    //        {
    //            StartLive();
    //        }
    //        else
    //        {
    //            StopLive();
    //        }
    //    }
    //}
}
