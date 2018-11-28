//
//  ResultsViewController.swift
//  PAMApp
//
//  Created by Jackson Quick on 11/27/18.
//  Copyright © 2018 Jackson Quick. All rights reserved.
//

import UIKit

class ResultsViewController: UIViewController {

    var resultText = ""
    @IBOutlet weak var results: UILabel!
    
    override func viewDidLoad() {
        super.viewDidLoad()
        // Do any additional setup after loading the view.
        results.text = self.resultText
    }


    /*
    // MARK: - Navigation

    // In a storyboard-based application, you will often want to do a little preparation before navigation
    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
        // Get the new view controller using segue.destination.
        // Pass the selected object to the new view controller.
    }
    */

}
