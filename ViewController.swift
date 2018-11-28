//
//  ViewController.swift
//  PAMApp
//
//  Created by Jackson Quick on 11/27/18.
//  Copyright © 2018 Jackson Quick. All rights reserved.
//

import UIKit

class ViewController: UIViewController {

    override func viewDidLoad() {
        super.viewDidLoad()
        // Do any additional setup after loading the view, typically from a nib.
    }

    @IBAction func onPressHome(_ sender: Any) {
        performSegue(withIdentifier: "segue", sender: self)
    }
    
}

