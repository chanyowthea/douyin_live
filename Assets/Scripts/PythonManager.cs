using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Net.Sockets;
using System.Net;
using UnityEngine;

public class PythonManager : MonoBehaviour
{
    bool mStartPython=false;

    void StartProcess()
    {
        //Kill_All_Python_Process();

        string fullPath = Application.dataPath + "/StreamingAssets/douyin_live/main.py";
        UnityEngine.Debug.Log(fullPath);

        // 设置命令行参数
        string command = "/c activate Python & python \"" + fullPath + "\"";

        // 创建ProcessStartInfo对象
        startInfo = new ProcessStartInfo();
        // 设定执行cmd
        startInfo.FileName = "cmd.exe";
        // 输入参数是上一步的command字符串
        startInfo.Arguments = command;
        // 因为嵌入Unity中后台使用，所以设置不显示窗口
        startInfo.CreateNoWindow = true;
        // 这里需要设定为false
        startInfo.UseShellExecute = false;
        // 设置重定向这个进程的标准输出流，用于直接被Unity C#捕获，从而实现 Python -> Unity 的通信
        startInfo.RedirectStandardOutput = true;
        // 设置重定向这个进程的标准报错流，用于在Unity的C#中进行Debug Python里的bug
        startInfo.RedirectStandardError = true;

        // 创建Process
        process = new Process();
        process.StartInfo = startInfo;
        process.Start();
        mStartPython = true;
    }


    void OnApplicationQuit()
    {
        // 结束所有Python进程
        Kill_All_Python_Process();
    }
    private ProcessStartInfo startInfo;
    private Process process;

    // Start is called before the first frame update
    void Start()
    {
        StartProcess();
    }

    public void Kill_All_Python_Process()
    {
        if (!mStartPython) { return; }

        Process[] allProcesses = Process.GetProcesses();
        for (int i = allProcesses.Length-1; i >= 0; i--)
        {
            try
            {
                var process_1 = allProcesses[i];
                string processName = process_1.ProcessName;
                if (processName.ToLower().Contains("python"))
                {
                    UnityEngine.Debug.LogFormat("Kill {0} {1}", processName, process_1.StartInfo.Arguments);
                    process_1.Kill();
                    break;
                }
            }
            catch (Exception ex)
            {
                // 处理异常
                print(ex);
            }
        }
    }
}
