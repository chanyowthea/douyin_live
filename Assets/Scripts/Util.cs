using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Text.RegularExpressions;
using UnityEngine;

public static class Util
{
    public static string Unicode2String(string source)
    {
        return new Regex(@"\\u([0-9A-F]{4})", RegexOptions.IgnoreCase).Replace(
             source, x => string.Empty + Convert.ToChar(Convert.ToUInt16(x.Result("$1"), 16)));
    }

    public static T GetData2<T>(string text) where T : class
    {
        //JsonData table = AnalysisJson.Analy<JsonData>(text);
        T t = JsonUtility.FromJson<T>(text);
        return t;
    }

    public static void DeleteChildAndFolder(string childItemPath)
    {
        DeleteFilesAndFolders(childItemPath);
        Debug.Log("DeleteChildAndFolder 删除完毕");
    }
    private static void DeleteFilesAndFolders(string path)
    {
        // Delete files.
        string[] files = Directory.GetFiles(path);
        foreach (var file in files)
        {
            File.Delete(file);
        }

        // Delete folders.
        string[] folders = Directory.GetDirectories(path);
        foreach (var folder in folders)
        {
            if (Directory.GetFiles(folder).Length <= 0)
            {
                Directory.Delete(folder);
            }
            else
            {
                DeleteFilesAndFolders(folder);
            }
        }
    }
}
