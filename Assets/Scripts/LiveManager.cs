using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class LiveManager : MonoBehaviour
{
    HTTPServer HTTPServer;
    [SerializeField] RectTransform mBG;
    [SerializeField] Text mLogText;
    string mLogMsg = "";
    int mCount = 0;
    int mMaxCount = 100;
    int mRemoveCount = 10;
    List<string> mMsgList = new List<string>();
    Queue<string> mMsgQueue = new Queue<string>();
    Coroutine mRoutine;

    void Start()
    {
        HTTPServer = GameObject.FindObjectOfType<HTTPServer>();
        mRoutine = StartCoroutine(ProcessMessage());
    }

    void OnDestroy()
    {
        if (mRoutine != null) { 
            StopCoroutine(mRoutine);
        }
        mRoutine = null;
    }

    public void ClearQueue()
    {
        mMsgQueue.Clear();
    }

    void RecalcLog()
    {
        mLogMsg = "";
        for (int i = 0; i < mMsgList.Count; i++)
        {
            var msg = mMsgList[i];
            mLogMsg += msg + "\n";
        }
    }

    public void AddLog(string msg)
    {
        // 顺手改个颜色
        msg = msg.Replace("[弹幕]", "<color=lightblue>[弹幕]</color>");
        msg = msg.Replace("[礼物]", "<color=red>[礼物]</color>");
        msg = msg.Replace("[关注]", "<color=cyan>[关注]</color>");
        msg = msg.Replace("[点赞]", "<color=orange>[点赞]</color>");
        msg = msg.Replace("[进入]", "<color=green>[进入]</color>");


        mMsgList.Add(msg);
        mCount += 1;
        if (mCount > mMaxCount)
        {
            mMsgList.RemoveRange(0, mRemoveCount);
            mCount -= mRemoveCount;
            //Debug.Log(string.Format("11111 AddLog==========={0} {1} {2} {3}", mMsgList.Count, mCount, mMaxCount, mRemoveCount));
            RecalcLog();
        }
        else
        {
            //Debug.Log(string.Format("AddLog==========={0} {1} {2} {3}", mMsgList.Count, mCount, mMaxCount, mRemoveCount));
            mLogMsg += msg + "\n";
        }

        mLogText.text = mLogMsg;
        
        if (mLogText.rectTransform.rect.height >= mBG.rect.height)
        {
            var pos = mLogText.rectTransform.anchoredPosition;
            pos.y = mLogText.rectTransform.rect.height - mBG.rect.height + 10;
            Canvas.ForceUpdateCanvases();
            mLogText.rectTransform.anchoredPosition = pos;
            Canvas.ForceUpdateCanvases();
        }
    }
    public void ClearLog(string msg)
    {
        mLogMsg = "";
        mLogText.text = mLogMsg;
    }

    IEnumerator ProcessMessage()
    {
        while (true)
        {
            var ms = HTTPServer.GetRecvMessages();
            //Debug.Log(ms.Count);
            for (int i = 0; i < ms.Count; i++)
            {
                mMsgQueue.Enqueue(ms[i]);
            }
            ms.Clear();
            if (mMsgQueue.Count > 0)
            {
                var m = mMsgQueue.Peek();
                mMsgQueue.Dequeue();
                AddLog(m);
            }
            yield return new WaitForSeconds(0.5f);
        }
    }
}
